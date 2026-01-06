
import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy import func, case
from sqlalchemy.orm import Session

import models

logger = logging.getLogger(__name__)


class ReportService:
    """
    Encapsulates all report‐generation logic.
    Each method takes a SQLAlchemy Session and returns a list of dicts
    with 'label' and 'value' (or in some cases more detailed records).
    """

    @staticmethod
    def station_unit_count(db: Session) -> List[Dict[str, Any]]:
        """
        1. Station-Wise Unit Count
        SELECT station_code, COUNT(unit_no) AS value
        FROM units
        GROUP BY station_code
        """
        logger.info("Generating report: Station-Wise Unit Count")
        results = (
            db.query(
                models.Unit.station_code.label("label"),
                func.count(models.Unit.unit_no).label("value"),
            )
            .group_by(models.Unit.station_code)
            .all()
        )
        return [{"label": r.label, "value": int(r.value)} for r in results]

    @staticmethod
    def station_total_license_fee(
        db: Session, top: bool = True, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        2/3. Top or Bottom Stations by Total License Fee
        SUM(license_fee) grouped by station_code, ordered desc (top) or asc (bottom)
        """
        direction = (
            func.sum(models.Unit.license_fee).desc()
            if top
            else func.sum(models.Unit.license_fee).asc()
        )
        logger.info(
            "Generating report: %s Stations by Total License Fee (limit=%d)",
            "Top" if top else "Bottom",
            limit,
        )
        results = (
            db.query(
                models.Unit.station_code.label("label"),
                func.coalesce(func.sum(models.Unit.license_fee), 0).label("value"),
            )
            .group_by(models.Unit.station_code)
            .order_by(direction)
            .limit(limit)
            .all()
        )
        return [{"label": r.label, "value": float(r.value)} for r in results]

    @staticmethod
    def station_total_earnings(db: Session) -> List[Dict[str, Any]]:
        """
        4. Station-Wise Total Earnings
        SUM(amount + gst) grouping by station_code
        """
        logger.info("Generating report: Station-Wise Total Earnings")
        total_expr = func.coalesce(func.sum(models.Earning.amount + models.Earning.gst), 0)
        results = (
            db.query(models.Earning.station_code.label("label"), total_expr.label("value"))
            .group_by(models.Earning.station_code)
            .all()
        )
        return [{"label": r.label, "value": float(r.value)} for r in results]

    @staticmethod
    def station_average_license_fee(db: Session) -> List[Dict[str, Any]]:
        """
        5. Station-Wise Average License Fee
        AVG(license_fee) grouped by station_code
        """
        logger.info("Generating report: Station-Wise Average License Fee")
        avg_expr = func.coalesce(func.avg(models.Unit.license_fee), 0)
        results = (
            db.query(models.Unit.station_code.label("label"), avg_expr.label("value"))
            .group_by(models.Unit.station_code)
            .all()
        )
        return [{"label": r.label, "value": float(r.value)} for r in results]

    @staticmethod
    def station_overdue_units(db: Session) -> List[Dict[str, Any]]:
        """
        6. Station-Wise Overdue Units
        COUNT(unit_no) where license_paid_upto < today, grouped by station_code
        """
        logger.info("Generating report: Station-Wise Overdue Units")
        today = date.today()
        results = (
            db.query(
                models.Unit.station_code.label("label"),
                func.count(models.Unit.unit_no).label("value"),
            )
            .filter(models.Unit.license_paid_upto < today)
            .group_by(models.Unit.station_code)
            .all()
        )
        return [{"label": r.label, "value": int(r.value)} for r in results]

    @staticmethod
    def station_upcoming_contract_expiry(
        db: Session, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        7. Station-Wise Upcoming Contract Expiry (next `days` days)
        COUNT(unit_no) where contract_to between today and today+days, grouped by station_code
        """
        logger.info(
            "Generating report: Station-Wise Upcoming Contract Expiry (next %d days)", days
        )
        today = date.today()
        cutoff = today + timedelta(days=days)
        results = (
            db.query(
                models.Unit.station_code.label("label"),
                func.count(models.Unit.unit_no).label("value"),
            )
            .filter(models.Unit.contract_to.between(today, cutoff))
            .group_by(models.Unit.station_code)
            .all()
        )
        return [{"label": r.label, "value": int(r.value)} for r in results]

    @staticmethod
    def station_payment_status(db: Session) -> List[Dict[str, Any]]:
        """
        8. Station-Wise Payment Status:
        For each station, count how many units are:
          - Paid   (license_paid_upto >= today + 30)
          - Upcoming (today <= license_paid_upto < today + 30)
          - Overdue (license_paid_upto < today)
          - Unpaid  (license_paid_upto IS NULL)
        Returns a list of dicts:
        [
          { "station": "ABC", "paid": 10, "upcoming": 5, "overdue": 2, "unpaid": 3 },
          ...
        ]
        """
        logger.info("Generating report: Station-Wise Payment Status")
        today = date.today()
        plus30 = today + timedelta(days=30)

        # Build CASE expressions for each bucket
        paid_case = func.sum(
            case(
                [(models.Unit.license_paid_upto >= plus30, 1)],
                else_=0,
            )
        )
        upcoming_case = func.sum(
            case(
                [
                    (models.Unit.license_paid_upto >= today, 1),
                    (models.Unit.license_paid_upto < plus30, 1),
                ],
                else_=0,
            )
        )
        overdue_case = func.sum(
            case(
                [(models.Unit.license_paid_upto < today, 1)],
                else_=0,
            )
        )
        unpaid_case = func.sum(
            case(
                [(models.Unit.license_paid_upto.is_(None), 1)],
                else_=0,
            )
        )

        results = (
            db.query(
                models.Unit.station_code.label("station"),
                paid_case.label("paid"),
                upcoming_case.label("upcoming"),
                overdue_case.label("overdue"),
                unpaid_case.label("unpaid"),
            )
            .group_by(models.Unit.station_code)
            .all()
        )

        output: List[Dict[str, Any]] = []
        for row in results:
            output.append(
                {
                    "station": row.station,
                    "paid": int(row.paid),
                    "upcoming": int(row.upcoming),
                    "overdue": int(row.overdue),
                    "unpaid": int(row.unpaid),
                }
            )
        return output

    @staticmethod
    def station_revenue_trend(
        db: Session, months: int = 6
    ) -> List[Dict[str, Any]]:
        """
        9. Station-Wise Revenue Trend over last `months` months
        For each station, produce a time series of (year-month, total earnings) for the last `months` months.
        Returns a list of:
        [
          { "station": "ABC", "period": "2023-02", "value": 12345.67 },
          ...
        ]
        """
        logger.info("Generating report: Station-Wise Revenue Trend (last %d months)", months)
        today = date.today()
        # Compute the earliest month
        start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        for _ in range(months - 1):
            start_date = (start_date - timedelta(days=1)).replace(day=1)

        # Extract year‐month from Earning.period_to (or use date_of_receipt if preferable).
        period_expr = func.strftime("%Y-%m", models.Earning.period_to)

        total_expr = func.coalesce(func.sum(models.Earning.amount + models.Earning.gst), 0)

        results = (
            db.query(
                models.Earning.station_code.label("station"),
                period_expr.label("period"),
                total_expr.label("value"),
            )
            .filter(models.Earning.period_to >= start_date)
            .group_by(models.Earning.station_code, period_expr)
            .order_by(models.Earning.station_code, period_expr)
            .all()
        )

        output: List[Dict[str, Any]] = []
        for row in results:
            output.append(
                {"station": row.station, "period": row.period, "value": float(row.value)}
            )
        return output

    @staticmethod
    def station_footfall_vs_revenue(db: Session) -> List[Dict[str, Any]]:
        """
        10. Station-Wise Footfall vs. Revenue
        For each station, return footfall (from Station) and total revenue (sum of Earning.amount+gst).
        Returns:
        [
          { "station": "ABC", "footfall": 1234, "revenue": 56789.01 },
          ...
        ]
        """
        logger.info("Generating report: Station-Wise Footfall vs Revenue")
        total_expr = func.coalesce(func.sum(models.Earning.amount + models.Earning.gst), 0)

        results = (
            db.query(
                models.Station.station_code.label("station"),
                models.Station.footfall.label("footfall"),
                total_expr.label("revenue"),
            )
            .outerjoin(models.Earning, models.Station.station_code == models.Earning.station_code)
            .group_by(models.Station.station_code, models.Station.footfall)
            .all()
        )

        output: List[Dict[str, Any]] = []
        for row in results:
            output.append(
                {"station": row.station, "footfall": int(row.footfall or 0), "revenue": float(row.revenue)}
            )
        return output

    @staticmethod
    def category_unit_count(db: Session) -> List[Dict[str, Any]]:
        """
        11. Categorization-Wise Unit Count
        COUNT(unit_no) grouped by Unit.reservation_cat
        """
        logger.info("Generating report: Category-Wise Unit Count")
        results = (
            db.query(
                models.Unit.reservation_cat.label("label"),
                func.count(models.Unit.unit_no).label("value"),
            )
            .group_by(models.Unit.reservation_cat)
            .all()
        )
        return [{"label": r.label or "Unspecified", "value": int(r.value)} for r in results]

    @staticmethod
    def category_overdue_units(db: Session) -> List[Dict[str, Any]]:
        """
        12. Category-Wise Overdue Units
        COUNT(unit_no) where license_paid_upto < today, grouped by reservation_cat
        """
        logger.info("Generating report: Category-Wise Overdue Units")
        today = date.today()
        results = (
            db.query(
                models.Unit.reservation_cat.label("label"),
                func.count(models.Unit.unit_no).label("value"),
            )
            .filter(models.Unit.license_paid_upto < today)
            .group_by(models.Unit.reservation_cat)
            .all()
        )
        return [{"label": r.label or "Unspecified", "value": int(r.value)} for r in results]

    @staticmethod
    def category_upcoming_contract_expiry(
        db: Session, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        13. Category-Wise Upcoming Contract Expiry (next `days` days)
        COUNT(unit_no) where contract_to between today and today+days, grouped by reservation_cat
        """
        logger.info(
            "Generating report: Category-Wise Upcoming Contract Expiry (next %d days)", days
        )
        today = date.today()
        cutoff = today + timedelta(days=days)
        results = (
            db.query(
                models.Unit.reservation_cat.label("label"),
                func.count(models.Unit.unit_no).label("value"),
            )
            .filter(models.Unit.contract_to.between(today, cutoff))
            .group_by(models.Unit.reservation_cat)
            .all()
        )
        return [{"label": r.label or "Unspecified", "value": int(r.value)} for r in results]

    @staticmethod
    def category_average_license_fee(db: Session) -> List[Dict[str, Any]]:
        """
        14. Category-Wise Average License Fee
        AVG(license_fee) grouped by reservation_cat
        """
        logger.info("Generating report: Category-Wise Average License Fee")
        avg_expr = func.coalesce(func.avg(models.Unit.license_fee), 0)
        results = (
            db.query(models.Unit.reservation_cat.label("label"), avg_expr.label("value"))
            .group_by(models.Unit.reservation_cat)
            .all()
        )
        return [{"label": r.label or "Unspecified", "value": float(r.value)} for r in results]

    @staticmethod
    def category_payment_status(db: Session) -> List[Dict[str, Any]]:
        """
        15. Category-Wise Payment Status
        For each reservation_cat, count units in Paid/Upcoming/Overdue/Unpaid categories.
        """
        logger.info("Generating report: Category-Wise Payment Status")
        today = date.today()
        plus30 = today + timedelta(days=30)

        paid_case = func.sum(case([(models.Unit.license_paid_upto >= plus30, 1)], else_=0))
        upcoming_case = func.sum(
            case(
                [(models.Unit.license_paid_upto >= today, 1), (models.Unit.license_paid_upto < plus30, 1)],
                else_=0,
            )
        )
        overdue_case = func.sum(case([(models.Unit.license_paid_upto < today, 1)], else_=0))
        unpaid_case = func.sum(case([(models.Unit.license_paid_upto.is_(None), 1)], else_=0))

        results = (
            db.query(
                models.Unit.reservation_cat.label("category"),
                paid_case.label("paid"),
                upcoming_case.label("upcoming"),
                overdue_case.label("overdue"),
                unpaid_case.label("unpaid"),
            )
            .group_by(models.Unit.reservation_cat)
            .all()
        )

        output: List[Dict[str, Any]] = []
        for row in results:
            output.append(
                {
                    "category": row.category or "Unspecified",
                    "paid": int(row.paid),
                    "upcoming": int(row.upcoming),
                    "overdue": int(row.overdue),
                    "unpaid": int(row.unpaid),
                }
            )
        return output

    @staticmethod
    def category_dead_units(db: Session) -> List[Dict[str, Any]]:
        """
        16. Dead Units by Category
        COUNT(units that never generated earnings), grouped by reservation_cat.
        A dead unit is one that does not appear in the Earning table.
        """
        logger.info("Generating report: Category-Wise Dead Units")
        subquery = (
            db.query(models.Earning.unit_no.distinct().label("unit_no"))
            .subquery()
        )
        results = (
            db.query(
                models.Unit.reservation_cat.label("label"),
                func.count(models.Unit.unit_no).label("value"),
            )
            .outerjoin(
                subquery, models.Unit.unit_no == subquery.c.unit_no
            )
            .filter(subquery.c.unit_no.is_(None))
            .group_by(models.Unit.reservation_cat)
            .all()
        )
        return [{"label": r.label or "Unspecified", "value": int(r.value)} for r in results]

    @staticmethod
    def earnings_by_payment_head(db: Session) -> List[Dict[str, Any]]:
        """
        17. Earnings by Payment Head
        SUM(amount+gst) grouped by payment_head
        """
        logger.info("Generating report: Earnings by Payment Head")
        total_expr = func.coalesce(func.sum(models.Earning.amount + models.Earning.gst), 0)
        results = (
            db.query(models.Earning.payment_head.label("label"), total_expr.label("value"))
            .group_by(models.Earning.payment_head)
            .all()
        )
        return [{"label": r.label or "Unspecified", "value": float(r.value)} for r in results]

    @staticmethod
    def earnings_by_zone(db: Session) -> List[Dict[str, Any]]:
        """
        18. Zone-Wise Total Earnings
        JOIN Earning → Station to get zone, then SUM(amount+gst) GROUP BY zone
        """
        logger.info("Generating report: Zone-Wise Total Earnings")
        total_expr = func.coalesce(func.sum(models.Earning.amount + models.Earning.gst), 0)
        results = (
            db.query(models.Station.zone.label("label"), total_expr.label("value"))
            .join(models.Station, models.Station.station_code == models.Earning.station_code)
            .group_by(models.Station.zone)
            .all()
        )
        return [{"label": r.label or "Unspecified", "value": float(r.value)} for r in results]

    @staticmethod
    def earnings_by_division(db: Session) -> List[Dict[str, Any]]:
        """
        19. Division-Wise Total Earnings
        JOIN Earning → Station to get division, then SUM(amount+gst) GROUP BY division
        """
        logger.info("Generating report: Division-Wise Total Earnings")
        total_expr = func.coalesce(func.sum(models.Earning.amount + models.Earning.gst), 0)
        results = (
            db.query(models.Station.division.label("label"), total_expr.label("value"))
            .join(models.Station, models.Station.station_code == models.Earning.station_code)
            .group_by(models.Station.division)
            .all()
        )
        return [{"label": r.label or "Unspecified", "value": float(r.value)} for r in results]

    @staticmethod
    def total_earnings_trend(db: Session, months: int = 12) -> List[Dict[str, Any]]:
        """
        20. Last `months` Months Revenue Trend (All Stations)
        SUM(amount+gst) per year-month, for the last `months` months
        """
        logger.info("Generating report: Last %d Months Revenue Trend (All Stations)", months)
        today = date.today()
        start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        for _ in range(months - 1):
            start_date = (start_date - timedelta(days=1)).replace(day=1)

        period_expr = func.strftime("%Y-%m", models.Earning.period_to)
        total_expr = func.coalesce(func.sum(models.Earning.amount + models.Earning.gst), 0)

        results = (
            db.query(period_expr.label("period"), total_expr.label("value"))
            .filter(models.Earning.period_to >= start_date)
            .group_by(period_expr)
            .order_by(period_expr)
            .all()
        )
        return [{"period": r.period, "value": float(r.value)} for r in results]

    @staticmethod
    def top_units_by_earnings(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        21. Top Units by Total Earnings
        SUM(amount+gst) grouped by unit_no, ordered desc limit `limit`
        """
        logger.info("Generating report: Top %d Units by Total Earnings", limit)
        total_expr = func.coalesce(func.sum(models.Earning.amount + models.Earning.gst), 0)
        results = (
            db.query(models.Earning.unit_no.label("label"), total_expr.label("value"))
            .group_by(models.Earning.unit_no)
            .order_by(total_expr.desc())
            .limit(limit)
            .all()
        )
        return [{"label": r.label, "value": float(r.value)} for r in results]

    @staticmethod
    def bottom_units_by_earnings(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        22. Bottom Units by Total Earnings
        SUM(amount+gst) grouped by unit_no, ordered asc limit `limit`
        """
        logger.info("Generating report: Bottom %d Units by Total Earnings", limit)
        total_expr = func.coalesce(func.sum(models.Earning.amount + models.Earning.gst), 0)
        results = (
            db.query(models.Earning.unit_no.label("label"), total_expr.label("value"))
            .group_by(models.Earning.unit_no)
            .order_by(total_expr.asc())
            .limit(limit)
            .all()
        )
        return [{"label": r.label, "value": float(r.value)} for r in results]

    @staticmethod
    def dead_units(db: Session) -> List[Dict[str, Any]]:
        """
        23. Units with No Earnings (Dead Units)
        List unit_no, station_code, licensee_name WHERE unit_no NOT IN Earning.unit_no
        """
        logger.info("Generating report: Units with No Earnings (Dead Units)")
        subquery = db.query(models.Earning.unit_no.distinct().label("unit_no")).subquery()
        results = (
            db.query(
                models.Unit.unit_no.label("unit_no"),
                models.Unit.station_code.label("station"),
                models.Unit.licensee_name.label("licensee"),
            )
            .outerjoin(subquery, models.Unit.unit_no == subquery.c.unit_no)
            .filter(subquery.c.unit_no.is_(None))
            .all()
        )
        return [
            {"unit_no": r.unit_no, "station": r.station, "licensee": r.licensee}
            for r in results
        ]

    @staticmethod
    def overall_payment_status_summary(db: Session) -> Dict[str, int]:
        """
        24. Overall Payment Status Summary
        Count all units in each bucket: Paid / Upcoming / Overdue / Unpaid
        """
        logger.info("Generating report: Overall Payment Status Summary")
        today = date.today()
        plus30 = today + timedelta(days=30)

        paid_count = (
            db.query(func.count(models.Unit.unit_no))
            .filter(models.Unit.license_paid_upto >= plus30)
            .scalar()
            or 0
        )
        upcoming_count = (
            db.query(func.count(models.Unit.unit_no))
            .filter(
                models.Unit.license_paid_upto >= today, models.Unit.license_paid_upto < plus30
            )
            .scalar()
            or 0
        )
        overdue_count = (
            db.query(func.count(models.Unit.unit_no))
            .filter(models.Unit.license_paid_upto < today)
            .scalar()
            or 0
        )
        unpaid_count = (
            db.query(func.count(models.Unit.unit_no))
            .filter(models.Unit.license_paid_upto.is_(None))
            .scalar()
            or 0
        )

        return {
            "paid": int(paid_count),
            "upcoming": int(upcoming_count),
            "overdue": int(overdue_count),
            "unpaid": int(unpaid_count),
        }

    @staticmethod
    def units_by_zone(db: Session) -> List[Dict[str, Any]]:
        """
        25. Units by Zone
        JOIN Unit → Station (by station_code), then COUNT(unit_no) GROUP BY zone
        """
        logger.info("Generating report: Units by Zone")
        results = (
            db.query(
                models.Station.zone.label("label"),
                func.count(models.Unit.unit_no).label("value"),
            )
            .join(models.Station, models.Station.station_code == models.Unit.station_code)
            .group_by(models.Station.zone)
            .all()
        )
        return [{"label": r.label or "Unspecified", "value": int(r.value)} for r in results]

    @staticmethod
    def units_by_division(db: Session) -> List[Dict[str, Any]]:
        """
        26. Units by Division
        JOIN Unit → Station (by station_code), then COUNT(unit_no) GROUP BY division
        """
        logger.info("Generating report: Units by Division")
        results = (
            db.query(
                models.Station.division.label("label"),
                func.count(models.Unit.unit_no).label("value"),
            )
            .join(models.Station, models.Station.station_code == models.Unit.station_code)
            .group_by(models.Station.division)
            .all()
        )
        return [{"label": r.label or "Unspecified", "value": int(r.value)} for r in results]

    @staticmethod
    def licensee_count_by_station(db: Session) -> List[Dict[str, Any]]:
        """
        27. Licensee Count by Station
        COUNT(DISTINCT licensee_name) GROUP BY unit.station_code
        """
        logger.info("Generating report: Licensee Count by Station")
        results = (
            db.query(
                models.Unit.station_code.label("label"),
                func.count(func.distinct(models.Unit.licensee_name)).label("value"),
            )
            .group_by(models.Unit.station_code)
            .all()
        )
        return [{"label": r.label, "value": int(r.value)} for r in results]

    @staticmethod
    def avg_30day_earnings_by_station(db: Session) -> List[Dict[str, Any]]:
        """
        28. Average 30-Day Earnings by Station
        For each station, SUM(amount+gst WHERE date_of_receipt >= today−30)/30
        """
        logger.info("Generating report: Average 30-Day Earnings by Station")
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)
        total_expr = func.coalesce(func.sum(models.Earning.amount + models.Earning.gst), 0)
        results = (
            db.query(
                models.Earning.station_code.label("station"),
                (total_expr / 30).label("value"),
            )
            .filter(models.Earning.date_of_receipt >= thirty_days_ago)
            .group_by(models.Earning.station_code)
            .all()
        )
        return [{"station": r.station, "value": float(r.value)} for r in results]

    @staticmethod
    def parking_availability(db: Session) -> List[Dict[str, Any]]:
        """
        29. Parking Availability
        COUNT(stations WHERE parking = TRUE) and COUNT(stations WHERE parking = FALSE)
        """
        logger.info("Generating report: Parking Availability")
        yes_count = (
            db.query(func.count(models.Station.station_code))
            .filter(models.Station.parking.is_(True))
            .scalar()
            or 0
        )
        no_count = (
            db.query(func.count(models.Station.station_code))
            .filter(models.Station.parking.is_(False))
            .scalar()
            or 0
        )
        return [
            {"label": "Yes", "value": int(yes_count)},
            {"label": "No", "value": int(no_count)},
        ]

    @staticmethod
    def station_sizes_by_platform_count(db: Session) -> List[Dict[str, Any]]:
        """
        30. Station Sizes by Platform Count
        Bucket station.platform_count into bins: 1, 2, 3-5, 6-10, >10
        """
        logger.info("Generating report: Station Sizes by Platform Count")

        # We can use CASE statements to bucket platform_count
        bucket_expr = case(
            [
                (models.Station.platform_count == 1, "1"),
                (models.Station.platform_count == 2, "2"),
                (models.Station.platform_count.between(3, 5), "3-5"),
                (models.Station.platform_count.between(6, 10), "6-10"),
                (models.Station.platform_count > 10, ">10"),
            ],
            else_="Unknown",
        )

        results = (
            db.query(bucket_expr.label("label"), func.count(models.Station.station_code).label("value"))
            .group_by(bucket_expr)
            .all()
        )
        return [{"label": r.label, "value": int(r.value)} for r in results]

    @staticmethod
    def revenue_per_ticket_by_station(db: Session) -> List[Dict[str, Any]]:
        """
        31. Revenue per Ticket by Station
        station.earnings_per_day / station.tkts_per_day
        """
        logger.info("Generating report: Revenue per Ticket by Station")
        # Only include stations where tkts_per_day > 0 to avoid division by zero
        results = (
            db.query(
                models.Station.station_code.label("station"),
                (models.Station.earnings_per_day / models.Station.tkts_per_day).label("value"),
            )
            .filter(models.Station.tkts_per_day.isnot(None), models.Station.tkts_per_day > 0)
            .all()
        )
        return [{"station": r.station, "value": float(r.value)} for r in results]