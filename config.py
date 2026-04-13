import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'argus-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///argus.db'  # Uses SQLite locally instead of PostgreSQL
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'static', 'images')
    AWS_BUCKET = os.environ.get('AWS_BUCKET', 'argus-images')