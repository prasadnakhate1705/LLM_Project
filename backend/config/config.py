import os

# Compute the project’s base directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Basic Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'changeme‑to‑a‑secure‑random‑value')
    DEBUG = False
    TESTING = False

    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'uploads')
    AUDIO_TEMP_DIR = os.path.join(UPLOAD_FOLDER, 'audio_temp')
    # Maximum upload size (in bytes). Adjust as needed.
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  

    # Video extensions we accept
    ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg'}

    # (Optional) Database settings, if you add one later
    # SQLALCHEMY_DATABASE_URI = os.getenv(
    #     'DATABASE_URL',
    #     'sqlite:///' + os.path.join(basedir, 'app.db')
    # )
    # SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
