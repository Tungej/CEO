from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'viewer' or 'uploader'

class DailyBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    bank_name = db.Column(db.String(50), nullable=False) # CBZ, Ecobank, etc.
    usd_balance = db.Column(db.Float, default=0.0)
    zig_balance = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Constraint to ensure one entry per bank per day
    __table_args__ = (db.UniqueConstraint('date', 'bank_name', name='_bank_date_uc'),)

class BankInterest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    paid = db.Column(db.Float, default=0.0)
    due = db.Column(db.Float, default=0.0)
    # Total is calculated: paid + due (or stored if preferred)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class AccountPayables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    creditors = db.Column(db.Float, default=0.0)
    creditors_project = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class AccountReceivables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    total_amount = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class ProductionMain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    
    # Billets
    unit_1_cumulative = db.Column(db.Float, default=0.0)
    unit_2_cumulative = db.Column(db.Float, default=0.0)
    
    # Rolling
    rolling_non_tmt = db.Column(db.Float, default=0.0)
    rolling_tmt = db.Column(db.Float, default=0.0)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductionSponge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    
    produced_tns = db.Column(db.Float, default=0.0)
    lost_tns = db.Column(db.Float, default=0.0)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class SalesData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    
    # New Product List
    angles_sales = db.Column(db.Float, default=0.0)
    flats_sales = db.Column(db.Float, default=0.0)
    window_sections_sales = db.Column(db.Float, default=0.0)
    fencing_standard_sales = db.Column(db.Float, default=0.0)
    channel_iron_sales = db.Column(db.Float, default=0.0)
    other_sections_sales = db.Column(db.Float, default=0.0)
    
    # Branches (Keeping these as they were)
    redcliff_sales = db.Column(db.Float, default=0.0)
    harare_sales = db.Column(db.Float, default=0.0)
    mutare_sales = db.Column(db.Float, default=0.0)
    bulawayo_sales = db.Column(db.Float, default=0.0)
    chiredzi_sales = db.Column(db.Float, default=0.0)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class GasPlantData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    
    # Consolidated Industrial Gas
    industrial_gases_cyl = db.Column(db.Float, default=0.0) 
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScrapData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    
    supplied_tns = db.Column(db.Float, default=0.0)
    total_purchased_tns = db.Column(db.Float, default=0.0)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class OperationalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    
    # Unit 1 Power Cut
    u1_hours = db.Column(db.Integer, default=0)
    u1_minutes = db.Column(db.Integer, default=0)
    
    # Unit 2 Power Cut
    u2_hours = db.Column(db.Integer, default=0)
    u2_minutes = db.Column(db.Integer, default=0)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)