#!/bin/bash

# Create the main project directory "backend"
mkdir -p backend

# Create subdirectories
echo "Creating directories..."
mkdir -p backend/config
mkdir -p backend/blueprints/job_blueprint
mkdir -p backend/blueprints/interview_blueprint
mkdir -p backend/blueprints/feedback_blueprint
mkdir -p backend/controllers
mkdir -p backend/services
mkdir -p backend/models
mkdir -p backend/utils
mkdir -p backend/tests

# Create the main files and empty source code files
echo "Creating files..."

# Entry point for Flask
touch backend/app.py

# Config files
touch backend/config/__init__.py
touch backend/config/config.py

# Blueprints
touch backend/blueprints/__init__.py

touch backend/blueprints/job_blueprint/__init__.py
touch backend/blueprints/job_blueprint/routes.py

touch backend/blueprints/interview_blueprint/__init__.py
touch backend/blueprints/interview_blueprint/routes.py

touch backend/blueprints/feedback_blueprint/__init__.py
touch backend/blueprints/feedback_blueprint/routes.py

# Controllers
touch backend/controllers/__init__.py
touch backend/controllers/job_controller.py
touch backend/controllers/interview_controller.py
touch backend/controllers/feedback_controller.py

# Services
touch backend/services/__init__.py
touch backend/services/job_scraper.py
touch backend/services/llm_integration.py
touch backend/services/video_processor.py
touch backend/services/facial_analysis.py
touch backend/services/gesture_analysis.py
touch backend/services/feedback_generator.py

# Models
touch backend/models/__init__.py
touch backend/models/job.py
touch backend/models/interview.py
touch backend/models/user.py
touch backend/models/answer.py

# Utils
touch backend/utils/__init__.py
touch backend/utils/logger.py
touch backend/utils/file_storage.py
touch backend/utils/helpers.py

# Tests
touch backend/tests/__init__.py
touch backend/tests/test_job_scraper.py
touch backend/tests/test_llm_integration.py
touch backend/tests/test_video_processor.py
touch backend/tests/test_feedback.py

# Other project files
touch backend/requirements.txt
touch backend/Dockerfile
touch backend/README.md

echo "File structure created successfully under the 'backend/' directory."
