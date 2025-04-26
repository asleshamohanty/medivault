from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from config import Config
import logging

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
Session(app)

# Configure logging
logging.basicConfig(
    level=app.config['LOG_LEVEL'],
    format=app.config['LOG_FORMAT']
)
logger = logging.getLogger(__name__)

# Import and register blueprints
from routes.auth import auth_bp
from routes.patient import patient_bp
from routes.doctor import doctor_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(patient_bp, url_prefix='/api/patient')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')

# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created")

if __name__ == '__main__':
    logger.info("Starting Medivault server...")
    app.run(debug=True)
