from flask import Flask
from flask_cors import CORS
from config.config import Config
from services.main import main_bp

def create_app():
    app = Flask(__name__)

    # Load configurations
    app.config.from_object(Config)

    # Enable CORS (adjust if needed for production)
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True
    )

    # Register blueprints
    app.register_blueprint(main_bp, url_prefix="/api")

    return app

# Entry point
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
