import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:orissA%4012@localhost:5432/medivault')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Session configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'medivault_secret_key_2024_secure')
SESSION_TYPE = 'filesystem'
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = SQLALCHEMY_TRACK_MODIFICATIONS
    
    # Session configuration
    SECRET_KEY = SECRET_KEY
    SESSION_TYPE = SESSION_TYPE
    PERMANENT_SESSION_LIFETIME = PERMANENT_SESSION_LIFETIME
    
    # Logging configuration
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
