import os
import subprocess
import openai
import json
from services.llm_integration import evaluate_answer

# Ensure your OpenAI API key is set in the environment
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_question_dir(interview_id: str, question_number: int) -> str:
    """
    Returns the directory path for storing files related to a specific question in an interview.
    """
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "static", "interviews", interview_id, f"question_{question_number}")
    )
    os.makedirs(base_dir, exist_ok=True)
    return base_dir


def extract_audio(video_path: str, audio_path: str) -> None:
    """
    Uses ffmpeg to extract a mono, 16kHz WAV audio file from the given video.
    Stores the result at the given audio_path.
    """
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]
    subprocess.run(cmd, check=True)


def transcribe_audio(audio_path: str) -> str:
    """
    Uses OpenAI Whisper (via the OpenAI API) to transcribe the given audio file.
    Returns the transcription text.
    """
    with open(audio_path, "rb") as audio_file:
        result = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
    return result.get("text", "").strip()


def process_video_answer(video_path: str, question_text: str, interview_id: str, question_number: int) -> dict:
    """
    Full pipeline:
      1. Store video under static folder
      2. Extract and save audio
      3. Transcribe and save transcript
      4. Evaluate and save feedback
    Returns paths and feedback results.
    """
    question_dir = get_question_dir(interview_id, question_number)

    # Move video to structured folder
    video_dest = os.path.join(question_dir, "video.mp4")
    os.replace(video_path, video_dest)

    # 1. Extract audio
    audio_path = os.path.join(question_dir, "audio.wav")
    extract_audio(video_dest, audio_path)

    try:
        # 2. Transcribe
        transcription = transcribe_audio(audio_path)

        # 3. Save transcript
        transcript_path = os.path.join(question_dir, "transcript.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcription)

        # 4. Evaluate
        feedback = evaluate_answer(transcription, question_text)

        # 5. Save feedback
        feedback_path = os.path.join(question_dir, "feedback.json")
        with open(feedback_path, "w", encoding="utf-8") as f:
            json.dump(feedback, f, indent=2)

        return {
            "transcription": transcription,
            "feedback": feedback,
            "question_dir": question_dir
        }

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
