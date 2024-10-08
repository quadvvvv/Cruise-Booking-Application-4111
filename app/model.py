from app import db
from sqlalchemy.orm import relationship

class Credentials(db.Model):
    __tablename__ = 'credentials'

    cred_id = db.Column(db.String, primary_key=True)
    cust_username = db.Column(db.String, unique=True, nullable=False)
    cust_password = db.Column(db.String, nullable=False)
    customer = relationship("Customer", back_populates="credentials", uselist=False)

class Customer(db.Model):
    __tablename__ = 'customers_cred'

    cust_id = db.Column(db.String, primary_key=True)
    cred_id = db.Column(db.String, db.ForeignKey('credentials.cred_id'), unique=True, nullable=False)
    cust_name = db.Column(db.String, nullable=False)
    cust_budget = db.Column(db.Float, nullable=False)
    cust_specialty = db.Column(db.String)
    cust_rating = db.Column(db.Float)
    
    credentials = relationship("Credentials", back_populates="customer")
    booking_records = relationship("BookingRecord", back_populates="customer")

class Company(db.Model):
    __tablename__ = 'companies'

    comp_id = db.Column(db.String, primary_key=True)
    comp_name = db.Column(db.String, nullable=False)
    comp_rating = db.Column(db.Float)
    
    cruises = relationship("Cruise", back_populates="company")
    booking_records = relationship("BookingRecord", back_populates="company")

class Cruise(db.Model):
    __tablename__ = 'cruises'

    cruise_id = db.Column(db.String, primary_key=True)
    comp_id = db.Column(db.String, db.ForeignKey('companies.comp_id'), nullable=False)
    cruise_name = db.Column(db.String, nullable=False)
    cruise_cost = db.Column(db.Float, nullable=False)
    cruise_capacity = db.Column(db.Integer)
    cruise_start_date = db.Column(db.Date, nullable=False)
    cruise_end_date = db.Column(db.Date, nullable=False)
    cruise_rating = db.Column(db.Float)

    company = relationship("Company", back_populates="cruises")
    booking_records = relationship("BookingRecord", back_populates="cruise")
    sail_to = relationship("Destination", secondary="sail_to", back_populates="cruises_to")
    sail_from = relationship("Destination", secondary="sail_from", back_populates="cruises_from")

class Destination(db.Model):
    __tablename__ = 'destinations'

    dest_id = db.Column(db.String, primary_key=True)
    dest_name = db.Column(db.String, nullable=False)
    dest_country = db.Column(db.String, nullable=False)
    dest_climate = db.Column(db.String)
    dest_specialty = db.Column(db.String)
    dest_is_domestic = db.Column(db.Boolean, default=True)

    cruises_to = relationship("Cruise", secondary="sail_to", back_populates="sail_to")
    cruises_from = relationship("Cruise", secondary="sail_from", back_populates="sail_from")

class SailTo(db.Model):
    __tablename__ = 'sail_to'

    cruise_id = db.Column(db.String, db.ForeignKey('cruises.cruise_id'), primary_key=True)
    dest_id = db.Column(db.String, db.ForeignKey('destinations.dest_id'), primary_key=True)

class SailFrom(db.Model):
    __tablename__ = 'sail_from'

    cruise_id = db.Column(db.String, db.ForeignKey('cruises.cruise_id'), primary_key=True)
    dest_id = db.Column(db.String, db.ForeignKey('destinations.dest_id'), primary_key=True)

class BookingRecord(db.Model):
    __tablename__ = 'booking_records'

    book_id = db.Column(db.String, primary_key=True)
    comp_id = db.Column(db.String, db.ForeignKey('companies.comp_id'), nullable=False)
    cust_id = db.Column(db.String, db.ForeignKey('customers_cred.cust_id'), nullable=False)
    cruise_id = db.Column(db.String, db.ForeignKey('cruises.cruise_id'), nullable=False)

    company = relationship("Company", back_populates="booking_records")
    customer = relationship("Customer", back_populates="booking_records")
    cruise = relationship("Cruise", back_populates="booking_records")