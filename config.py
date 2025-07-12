import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'swap.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'profile_pics')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max upload size
    PROFILE_PIC_RESOLUTION = (200, 200)