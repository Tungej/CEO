import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    # System Keys
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database (This will read from the server settings)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email Settings
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    # Read email credentials from hidden environment
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Read CC list from environment
    MAIL_CC = os.environ.get('MAIL_CC')
    
    SCHEDULER_API_ENABLED = True