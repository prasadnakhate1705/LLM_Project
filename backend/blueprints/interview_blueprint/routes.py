import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from services.video_processor import process_video_answer

interview_bp = Blueprint('interview', __name__)

# where to store uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@interview_bp.route('/submit_answer', methods=['POST'])
def submit_answer():
    """
    Receives a video file and question_index from the frontend,
    saves it locally, calls the video processing service, and returns the result.
    """
    # 1. Validate file
    if 'video' not in request.files:
        return jsonify({"error": "No video part"}), 400

    file = request.files['video']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid video file"}), 400

    # 2. Save file
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    # 3. (Optional) get metadata
    question_idx = request.form.get('question_index', None)

    # 4. Process video (delegated to your service)
    #    process_video_answer should return whatever analysis/feedback you need
    try:
        feedback = process_video_answer(save_path, question_idx)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 5. Return JSON response to frontend
    return jsonify({
        "message": "Video processed successfully",
        "question_index": question_idx,
        "feedback": feedback
    }), 200
