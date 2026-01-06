from decimal import Decimal
from pydantic import BaseModel, Field
from typing import ClassVar, Optional
from datetime import date

class StationBase(BaseModel):
    station_code: str
    station_name: str
    division: Optional[str] = None
    zone: Optional[str] = None
    section: Optional[str] = None
    cmi: Optional[str] = None
    den: Optional[str] = None
    sr_den: Optional[str] = None
    categorisation: Optional[str] = None
    earnings_range: Optional[str] = None
    passenger_range: Optional[str] = None
    footfall: Optional[int] = None
    platforms: Optional[str] = None
    platform_count: Optional[int] = None
    platform_type: Optional[str] = None
    parking: Optional[bool] = None
    pay_and_use: Optional[bool] = None

class StationCreate(StationBase):
    pass

class Station(StationBase):
    class Config:
        from_attributes = True

# --------------------
class UnitBase(BaseModel):
    unit_no: Optional[str] = None
    type_of_unit: Optional[str] = None
    station_code: Optional[str] = None
    station_category: Optional[str] = None
    pf_no: Optional[str] = None
    pegged_location: Optional[str] = None
    reservation_cat: Optional[str] = None
    type_of_allotment: Optional[str] = None
    licensee_name: Optional[str] = None
    license_fee: Optional[float] = None
    contract_from: Optional[date] = None
    contract_to: Optional[date] = None
    license_paid_upto: Optional[date] = None  # made optional with default None
    unit_status: Optional[str] = None

class UnitCreate(UnitBase):
    pass

class Unit(UnitBase):
    class Config:
        from_attributes = True

# --------------------
class EarningBase(BaseModel):
    date_of_receipt: Optional[date] = None
    unit_no: str
    station_code: str
    pf_no: Optional[str] = None
    licensee_name: Optional[str] = None
    payment_head: Optional[str] = None
    payment_sub_head: Optional[str] = None
    period_from: Optional[date] = None
    period_to: Optional[date] = None
    amount: Optional[float] = None
    gst: Optional[float] = None
    receipt_no: Optional[str] = None
    mr_date: Optional[date] = None
    ua_case: Optional[bool] = None
    remarks: Optional[str] = None

class EarningCreate(EarningBase):
    pass

class Earning(EarningBase):
    earning_id: int

    class Config:
        from_attributes = True


class DivisionSummary(BaseModel):
    division: Optional[str]
    station_count: int
    total_footfall: int

class EarningTotal(BaseModel):
    total: float

# (you can also add a small filter model if you like)
class EarningFilterParams(BaseModel):
    BaseModel: ClassVar[type] = BaseModel
    date_from: Optional[date]
    date_to:   Optional[date]
    unit_no:   Optional[str]

    from pydantic import BaseModel
from typing import Optional

class TimeSeriesPoint(BaseModel):
    period: str        # e.g. "2025-04"
    value: float

class LabelValue(BaseModel):
    label: Optional[str]
    value: float


from pydantic import BaseModel
from datetime import date
from typing import List

class OverdueUnit(BaseModel):
    unit_no: str
    license_paid_upto: date
    days_overdue: int

class ExpiringUnit(BaseModel):
    unit_no: str
    license_paid_upto: date
    days_until_expiry: int

class MonthlyEarning(BaseModel):
    station_code: str
    year: int
    month: int
    total_amount: float

class StationTrendPoint(BaseModel):
    date: date
    total_amount: float

class TrendSeries(BaseModel):
    station_code: str
    points: List[StationTrendPoint]


class EarningsTrendOut(BaseModel):
    period: str     # e.g. "2024-01"
    value: Decimal  # summed amount

    class Config:
        from_mode = True

class DatedRemark(BaseModel):
    date: date
    eng: Optional[str]
    electrical: Optional[str]
    snt: Optional[str]
    trd: Optional[str]

class LOARemarks(BaseModel):
    loa_issued_on: Optional[str]
    loa_value: Optional[str]
    agency_name: Optional[str]
    physical_progress: Optional[str]
    financial_progress: Optional[str]
    tdc: Optional[str]
    reassons_for_delay_if_any: Optional[str] = Field(None, alias="reassons_for_delay_(if_any)")

class RemarksBlock(BaseModel):
    engineering: Optional[LOARemarks]
    electrical_g: Optional[LOARemarks]
    electrical_trd: Optional[LOARemarks]
    snt: Optional[LOARemarks]
    additional: List[DatedRemark] = Field(default_factory=list)

class WorkEntryCreate(BaseModel):
    sn: Optional[int]
    pid: Optional[str]
    ph: Optional[int]
    year_of_sanction: str
    date_of_sanction: Optional[str]
    status: str
    is_umbrella: bool
    parent_umbrella_work: Optional[str]
    name_of_work: str
    executing_agency: Optional[str]

    cost_engg: float = 0
    cost_elec_g: float = 0
    cost_snt: float = 0
    cost_trd: float = 0
    cost_other: float = 0

    total_expenditure: float = 0
    financial_progress: float = 0
    physical_progress: float = 0

    remarks: Optional[RemarksBlock]
    station_codes: List[str]

class WorkEntryOut(WorkEntryCreate):
    id: int

    class Config:
        from_mode = True