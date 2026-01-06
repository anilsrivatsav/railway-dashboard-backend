from sqlalchemy import Column, Float, String, Integer, Boolean, Table, Text, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Station(Base):
    __tablename__ = 'stations'
    station_code = Column(String, primary_key=True, index=True)
    station_name = Column(String, nullable=False)
    division = Column(String)
    zone = Column(String)
    section = Column(String)
    cmi = Column(String)
    den = Column(String)
    sr_den = Column(String)
    categorisation = Column(String)
    earnings_range = Column(String)
    passenger_range = Column(String)
    footfall = Column(Integer)
    platforms = Column(String)
    platform_count = Column(Integer)
    platform_type = Column(String)
    parking = Column(Boolean)
    pay_and_use = Column(Boolean)
    no_of_trains_dealt = Column(Integer)
    tkts_per_day = Column(Integer)
    pass_per_day = Column(Integer)
    earnings_per_day = Column(DECIMAL(12, 2))
    footfalls_per_day = Column(Integer)
    units = relationship("Unit", back_populates="station", cascade="all, delete")
    earnings = relationship("Earning", back_populates="station", cascade="all, delete")

class Unit(Base):
    __tablename__ = 'units'
    unit_no = Column(String, primary_key=True, index=True)
    type_of_unit = Column(String)
    station_code = Column(String, ForeignKey('stations.station_code'))
    station_category = Column(String)
    old_category = Column(String)
    pf_no = Column(String)
    pegged_location = Column(Text)
    reservation_cat = Column(String)
    type_of_allotment = Column(String)
    licensee_name = Column(String)
    license_fee = Column(DECIMAL(12, 2))
    license_paid_upto = Column(Date, nullable=True)
    contract_from = Column(Date)
    contract_to = Column(Date)
    unit_status = Column(String)
    station = relationship("Station", back_populates="units")
    earnings = relationship("Earning", back_populates="unit", cascade="all, delete")

class Earning(Base):
    __tablename__ = 'earnings'
    earning_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_of_receipt = Column(Date, nullable=True)
    unit_no = Column(String, ForeignKey('units.unit_no'))
    station_code = Column(String, ForeignKey('stations.station_code'))
    pf_no = Column(String)
    licensee_name = Column(String)
    payment_head = Column(String)
    payment_sub_head = Column(String)
    period_from = Column(Date)
    period_to = Column(Date)
    amount = Column(DECIMAL(12, 2))
    gst = Column(DECIMAL(12, 2))
    receipt_type = Column(String)
    receipt_no = Column(String)
    mr_date = Column(Date)
    ua_case = Column(Boolean)
    remarks = Column(Text)
    unit = relationship("Unit", back_populates="earnings")
    station = relationship("Station", back_populates="earnings")

    # backend/models.py

# Association table for WorkEntry ↔ Station (many-to-many)
workentry_stations = Table(
    'workentry_stations', Base.metadata,
    Column('workentry_id', Integer, ForeignKey('workentry.id')),
    Column('station_code', String, ForeignKey('stations.station_code'))  # ✅ fixed here
)
class WorkEntry(Base):
    __tablename__ = "workentry"

    id = Column(Integer, primary_key=True, index=True)
    sn = Column(Integer)
    pid = Column(String)
    ph = Column(Integer)
    year_of_sanction = Column(String)
    date_of_sanction = Column(String)
    status = Column(String)
    is_umbrella = Column(Boolean)
    parent_umbrella_work = Column(String)
    name_of_work = Column(String)
    executing_agency = Column(String)

    cost_engg = Column(Float, default=0)
    cost_elec_g = Column(Float, default=0)
    cost_snt = Column(Float, default=0)
    cost_trd = Column(Float, default=0)
    cost_other = Column(Float, default=0)

    total_expenditure = Column(Float, default=0)
    financial_progress = Column(Float, default=0)
    physical_progress = Column(Float, default=0)

    remarks_engineering = Column(Text)
    remarks_electrical_g = Column(Text)
    remarks_electrical_trd = Column(Text)
    remarks_snt = Column(Text)

    stations = relationship("Station", secondary=workentry_stations, backref="works")