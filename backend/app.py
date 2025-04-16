from flask import Flask
from config.config import Config
from blueprints.job_blueprint import job_bp
from blueprints.interview_blueprint import interview_bp
from blueprints.feedback_blueprint import feedback_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(job_bp, url_prefix='/jobs')
    app.register_blueprint(interview_bp, url_prefix='/interview')
    app.register_blueprint(feedback_bp, url_prefix='/feedback')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
