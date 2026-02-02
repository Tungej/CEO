import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    # Use the variable from the .env file
    # If the file isn't found, it defaults to None or the second argument
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@localhost:5433/kpi_portal'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'it@smlzim.com'
    
    # --- HERE IS THE CHANGE ---
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    MAIL_DEFAULT_SENDER = 'it@smlzim.com'
    MAIL_CC = 'upendra.a@smlzim.com, lewis.k@smlzim.com, julius.t@smlzim.com'
    
    SCHEDULER_API_ENABLED = True