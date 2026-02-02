import os

class Config:
    SECRET_KEY = 'qwertqweQ#1'
    
    # Database Connection
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@localhost:5433/OPDB'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
     # --- EMAIL SETTINGS (Office 365) ---
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    MAIL_USERNAME = 'it@smlzim.com'
    MAIL_PASSWORD = 'Mponda@J2026'  # (Please change this if it's your real login!)
    
    # >>> YOU WERE MISSING THIS LINE BELOW <<<
    MAIL_DEFAULT_SENDER = 'it@smlzim.com'
    
    # >>> ADD THIS LINE <<<
    MAIL_CC = 'upendra.a@smlzim.com, lewis.k@smlzim.com, julius.t@smlzim.com'  # The email you want to CC

    # Scheduler API Enabled
    SCHEDULER_API_ENABLED = True