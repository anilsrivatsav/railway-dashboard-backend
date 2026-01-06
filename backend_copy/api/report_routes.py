import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from services.report_service import ReportService
from database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/station-unit-count", response_model=List[Dict[str, Any]])
def station_unit_count_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.station_unit_count(db)
        return data
    except Exception as e:
        logger.exception("Error generating station_unit_count_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Station-Wise Unit Count report.",
        )


@router.get(
    "/station-license-fee-top", response_model=List[Dict[str, Any]]
)
def top_stations_by_license_fee(
    limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)
):
    try:
        data = ReportService.station_total_license_fee(db, top=True, limit=limit)
        return data
    except Exception:
        logger.exception("Error generating top_stations_by_license_fee")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Top Stations by License Fee report.",
        )


@router.get(
    "/station-license-fee-bottom", response_model=List[Dict[str, Any]]
)
def bottom_stations_by_license_fee(
    limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)
):
    try:
        data = ReportService.station_total_license_fee(db, top=False, limit=limit)
        return data
    except Exception:
        logger.exception("Error generating bottom_stations_by_license_fee")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Bottom Stations by License Fee report.",
        )


@router.get("/station-total-earnings", response_model=List[Dict[str, Any]])
def station_total_earnings_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.station_total_earnings(db)
        return data
    except Exception:
        logger.exception("Error generating station_total_earnings_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Station-Wise Total Earnings report.",
        )


@router.get("/station-average-license-fee", response_model=List[Dict[str, Any]])
def station_average_license_fee_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.station_average_license_fee(db)
        return data
    except Exception:
        logger.exception("Error generating station_average_license_fee_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Station-Wise Average License Fee report.",
        )


@router.get("/station-overdue-units", response_model=List[Dict[str, Any]])
def station_overdue_units_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.station_overdue_units(db)
        return data
    except Exception:
        logger.exception("Error generating station_overdue_units_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Station-Wise Overdue Units report.",
        )


@router.get("/station-upcoming-contract-expiry", response_model=List[Dict[str, Any]])
def station_upcoming_contract_expiry_report(
    days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)
):
    try:
        data = ReportService.station_upcoming_contract_expiry(db, days=days)
        return data
    except Exception:
        logger.exception("Error generating station_upcoming_contract_expiry_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Station-Wise Upcoming Contract Expiry report.",
        )


@router.get("/station-payment-status", response_model=List[Dict[str, Any]])
def station_payment_status_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.station_payment_status(db)
        return data
    except Exception:
        logger.exception("Error generating station_payment_status_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Station-Wise Payment Status report.",
        )


@router.get("/station-revenue-trend", response_model=List[Dict[str, Any]])
def station_revenue_trend_report(
    months: int = Query(6, ge=1, le=36), db: Session = Depends(get_db)
):
    try:
        data = ReportService.station_revenue_trend(db, months=months)
        return data
    except Exception:
        logger.exception("Error generating station_revenue_trend_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Station-Wise Revenue Trend report.",
        )


@router.get("/station-footfall-vs-revenue", response_model=List[Dict[str, Any]])
def station_footfall_vs_revenue_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.station_footfall_vs_revenue(db)
        return data
    except Exception:
        logger.exception("Error generating station_footfall_vs_revenue_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Station-Wise Footfall vs Revenue report.",
        )


@router.get("/category-unit-count", response_model=List[Dict[str, Any]])
def category_unit_count_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.category_unit_count(db)
        return data
    except Exception:
        logger.exception("Error generating category_unit_count_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Category-Wise Unit Count report.",
        )


@router.get("/category-overdue-units", response_model=List[Dict[str, Any]])
def category_overdue_units_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.category_overdue_units(db)
        return data
    except Exception:
        logger.exception("Error generating category_overdue_units_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Category-Wise Overdue Units report.",
        )


@router.get(
    "/category-upcoming-contract-expiry", response_model=List[Dict[str, Any]]
)
def category_upcoming_contract_expiry_report(
    days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)
):
    try:
        data = ReportService.category_upcoming_contract_expiry(db, days=days)
        return data
    except Exception:
        logger.exception("Error generating category_upcoming_contract_expiry_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Category-Wise Upcoming Contract Expiry report.",
        )


@router.get("/category-average-license-fee", response_model=List[Dict[str, Any]])
def category_average_license_fee_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.category_average_license_fee(db)
        return data
    except Exception:
        logger.exception("Error generating category_average_license_fee_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Category-Wise Average License Fee report.",
        )


@router.get("/category-payment-status", response_model=List[Dict[str, Any]])
def category_payment_status_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.category_payment_status(db)
        return data
    except Exception:
        logger.exception("Error generating category_payment_status_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Category-Wise Payment Status report.",
        )


@router.get("/category-dead-units", response_model=List[Dict[str, Any]])
def category_dead_units_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.category_dead_units(db)
        return data
    except Exception:
        logger.exception("Error generating category_dead_units_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Category-Wise Dead Units report.",
        )


@router.get("/earnings-by-payment-head", response_model=List[Dict[str, Any]])
def earnings_by_payment_head_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.earnings_by_payment_head(db)
        return data
    except Exception:
        logger.exception("Error generating earnings_by_payment_head_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Earnings by Payment Head report.",
        )


@router.get("/earnings-by-zone", response_model=List[Dict[str, Any]])
def earnings_by_zone_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.earnings_by_zone(db)
        return data
    except Exception:
        logger.exception("Error generating earnings_by_zone_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Zone-Wise Total Earnings report.",
        )


@router.get("/earnings-by-division", response_model=List[Dict[str, Any]])
def earnings_by_division_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.earnings_by_division(db)
        return data
    except Exception:
        logger.exception("Error generating earnings_by_division_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Division-Wise Total Earnings report.",
        )


@router.get("/earnings-trend", response_model=List[Dict[str, Any]])
def earnings_trend_report(
    months: int = Query(12, ge=1, le=36), db: Session = Depends(get_db)
):
    try:
        data = ReportService.total_earnings_trend(db, months=months)
        return data
    except Exception:
        logger.exception("Error generating earnings_trend_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Earnings Trend report.",
        )


@router.get("/top-units", response_model=List[Dict[str, Any]])
def top_units_report(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    try:
        data = ReportService.top_units_by_earnings(db, limit=limit)
        return data
    except Exception:
        logger.exception("Error generating top_units_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Top Units by Earnings report.",
        )


@router.get("/bottom-units", response_model=List[Dict[str, Any]])
def bottom_units_report(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    try:
        data = ReportService.bottom_units_by_earnings(db, limit=limit)
        return data
    except Exception:
        logger.exception("Error generating bottom_units_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Bottom Units by Earnings report.",
        )


@router.get("/dead-units", response_model=List[Dict[str, Any]])
def dead_units_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.dead_units(db)
        return data
    except Exception:
        logger.exception("Error generating dead_units_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Dead Units report.",
        )


@router.get("/payment-status-summary", response_model=Dict[str, int])
def payment_status_summary_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.overall_payment_status_summary(db)
        return data
    except Exception:
        logger.exception("Error generating payment_status_summary_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Overall Payment Status Summary report.",
        )


@router.get("/units-by-zone", response_model=List[Dict[str, Any]])
def units_by_zone_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.units_by_zone(db)
        return data
    except Exception:
        logger.exception("Error generating units_by_zone_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Units by Zone report.",
        )


@router.get("/units-by-division", response_model=List[Dict[str, Any]])
def units_by_division_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.units_by_division(db)
        return data
    except Exception:
        logger.exception("Error generating units_by_division_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Units by Division report.",
        )


@router.get("/licensee-count-by-station", response_model=List[Dict[str, Any]])
def licensee_count_by_station_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.licensee_count_by_station(db)
        return data
    except Exception:
        logger.exception("Error generating licensee_count_by_station_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Licensee Count by Station report.",
        )


@router.get("/avg-30day-earnings-by-station", response_model=List[Dict[str, Any]])
def avg_30day_earnings_by_station_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.avg_30day_earnings_by_station(db)
        return data
    except Exception:
        logger.exception("Error generating avg_30day_earnings_by_station_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Average 30-Day Earnings by Station report.",
        )


@router.get("/parking-availability", response_model=List[Dict[str, Any]])
def parking_availability_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.parking_availability(db)
        return data
    except Exception:
        logger.exception("Error generating parking_availability_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Parking Availability report.",
        )


@router.get("/station-sizes-by-platform-count", response_model=List[Dict[str, Any]])
def station_sizes_by_platform_count_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.station_sizes_by_platform_count(db)
        return data
    except Exception:
        logger.exception("Error generating station_sizes_by_platform_count_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Station Sizes by Platform Count report.",
        )


@router.get("/revenue-per-ticket-by-station", response_model=List[Dict[str, Any]])
def revenue_per_ticket_by_station_report(db: Session = Depends(get_db)):
    try:
        data = ReportService.revenue_per_ticket_by_station(db)
        return data
    except Exception:
        logger.exception("Error generating revenue_per_ticket_by_station_report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Revenue per Ticket by Station report.",
        )
