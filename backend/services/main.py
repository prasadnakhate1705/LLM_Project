import os
import uuid
from flask import Blueprint, request, jsonify
from services.resume_parser import extract_resume_text
from services.llm_integration import generate_questions, evaluate_answer
from services.video_processor import process_video_answer

# Blueprint for all routes
main_bp = Blueprint("main", __name__)

# Session context
SESSIONS = {}

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
TEMP_VIDEO_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "temp_videos"))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_VIDEO_FOLDER, exist_ok=True)

# Helper function: load difficulty persona text
def load_persona(level):
    level = level.lower()
    mode_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "Modes", f"{level.capitalize()}.txt"))
    if not os.path.exists(mode_file):
        raise FileNotFoundError(f"Persona mode file not found: {mode_file}")
    with open(mode_file, "r", encoding="utf-8") as f:
        return f.read().strip()


# === 1. Upload Resume ===
@main_bp.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "Resume file is required"}), 400

    file = request.files['resume']
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF resumes are accepted"}), 400

    session_id = str(uuid.uuid4())
    resume_text = extract_resume_text(file)

    # Save session state
    SESSIONS[session_id] = {
        "resume_text": resume_text,
        "job_description": None,
        "questions": [],
        "current_question_index": 0,
        "persona": None,
        "question_type": None,
    }

    return jsonify({"message": "Resume uploaded successfully", "session_id": session_id}), 200


# === 2. Upload Job Description ===
@main_bp.route('/api/upload_job_description', methods=['POST'])
def upload_job_description():
    data = request.json
    session_id = data.get("session_id")
    job_description = data.get("job_description")

    if not session_id or not job_description:
        return jsonify({"error": "Session ID and job description are required"}), 400

    if session_id not in SESSIONS:
        return jsonify({"error": "Invalid session ID"}), 400

    SESSIONS[session_id]["job_description"] = job_description

    return jsonify({"message": "Job description saved successfully"}), 200


# === 3. Generate Questions Based on Selections ===
@main_bp.route('/api/generate_questions', methods=['POST'])
def generate_interview_questions():
    data = request.json
    session_id = data.get("session_id")
    level = data.get("level")  # Easy, Medium, Hard
    question_type = data.get("question_type")  # resume, technical, behavioral

    if not session_id or not level or not question_type:
        return jsonify({"error": "Session ID, level, and question type are required"}), 400

    session = SESSIONS.get(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 400

    persona_text = load_persona(level)
    resume_text = session["resume_text"]
    job_description = session["job_description"]

    # Generate questions
    questions = generate_questions(
        job_description=job_description,
        resume=resume_text,
        prompt_type=question_type,
        persona=level.lower(),
        num_questions=5
    )

    # Update session
    session["questions"] = questions
    session["persona"] = level.lower()
    session["question_type"] = question_type

    return jsonify({
        "message": "Questions generated successfully",
        "questions_count": len(questions),
        "first_question": questions[0] if questions else None
    }), 200

# === 4. Get Next Question ===
@main_bp.route('/api/next_question', methods=['POST'])
def next_question():
    data = request.json
    session_id = data.get("session_id")

    session = SESSIONS.get(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 400

    index = session["current_question_index"]
    questions = session["questions"]

    if index >= len(questions):
        return jsonify({"finished": True, "message": "All questions completed!"}), 200

    question = questions[index]
    session["current_question_index"] += 1

    return jsonify({
        "finished": False,
        "question_number": index + 1,
        "question": question
    }), 200

# === 5. Submit Answer (Video) ===
@main_bp.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    if 'video' not in request.files:
        return jsonify({"error": "Video file is required"}), 400

    session_id = request.form.get("session_id")
    question_number = int(request.form.get("question_number"))

    session = SESSIONS.get(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 400

    video_file = request.files['video']
    temp_video_path = os.path.join(TEMP_VIDEO_FOLDER, f"{session_id}_q{question_number}.mp4")
    video_file.save(temp_video_path)

    question_text = session["questions"][question_number - 1]

    result = process_video_answer(
        video_path=temp_video_path,
        question_text=question_text,
        interview_id=session_id,
        question_number=question_number
    )

    return jsonify(result), 200

# === Optional: Summary or Final Endpoint Later ===
@main_bp.route('/api/session_summary', methods=['POST'])
def session_summary():
    data = request.json
    session_id = data.get("session_id")
    session = SESSIONS.get(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 400

    return jsonify({
        "session_id": session_id,
        "questions_answered": session["current_question_index"],
        "total_questions": len(session["questions"]),
        "message": "Session summary generated successfully."
    }), 200
