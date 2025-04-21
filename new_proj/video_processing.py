import os
import json
import whisper
import ffmpeg
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Whisper model once
try:
    MODEL = whisper.load_model("base")
    logger.info("Loaded Whisper model 'base'.")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    MODEL = None

# Local Python-based video → audio → timestamped transcript using ffmpeg-python


import os
import json
import whisper
import ffmpeg
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Whisper model once
try:
    MODEL = whisper.load_model("base")
    logger.info("Loaded Whisper model 'base'.")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    MODEL = None

def process_video(video_path: str):
    """
    1. Extracts audio (WAV) from the given video file using ffmpeg-python.
    2. Runs Whisper locally to produce a simple transcript (no timestamps).
    3. Saves the audio in /audio and the transcript text in /transcripts (as JSON with a 'text' key).

    Returns:
        audio_path (str)
        transcript_path (str)
    """
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    base_dir = os.getcwd()
    audio_dir = os.path.join(base_dir, 'audio')
    transcript_dir = os.path.join(base_dir, 'transcripts')
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(transcript_dir, exist_ok=True)

    # 1. Extract audio
    audio_path = os.path.join(audio_dir, f"{base_name}.wav")
    logger.info(f"Extracting audio to {audio_path}...")
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info("Audio extraction complete.")
    except ffmpeg.Error as e:
        err = e.stderr.decode() if hasattr(e, 'stderr') else str(e)
        logger.error(f"ffmpeg extraction error: {err}")
        raise

    if not os.path.exists(audio_path):
        msg = f"Audio not found at {audio_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    # 2. Simple Whisper transcription
    if MODEL is None:
        raise RuntimeError("Whisper model not loaded.")
    logger.info("Running simple transcription (no timestamps)...")
    try:
        result = MODEL.transcribe(audio_path)  # returns {'text': ..., ...}
        transcript_text = result.get('text', '').strip()
        logger.info("Transcription complete.")
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise

    # 3. Save transcript
    transcript_path = os.path.join(transcript_dir, f"{base_name}.json")
    try:
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump({"text": transcript_text}, f, ensure_ascii=False, indent=2)
        logger.info(f"Transcript saved to {transcript_path}.")
    except Exception as e:
        logger.error(f"Failed to save transcript: {e}")
        raise

    return audio_path, transcript_path

# def process_video(video_path: str):
#     """
#     1. Extracts audio (WAV) from the given video file using ffmpeg-python.
#     2. Runs Whisper locally to transcribe with word-level timestamps.
#     3. Saves the audio and transcript in root-level /audio and /transcripts directories.

#     Returns:
#         audio_path (str): Path to the extracted audio file.
#         transcript_path (str): Path to the JSON transcript file.
#     """
#     base_name = os.path.splitext(os.path.basename(video_path))[0]

#     # Use project root (cwd) for storage
#     base_dir = os.getcwd()
#     audio_dir = os.path.join(base_dir, 'audio')
#     transcript_dir = os.path.join(base_dir, 'transcripts')
#     os.makedirs(audio_dir, exist_ok=True)
#     os.makedirs(transcript_dir, exist_ok=True)

#     # 1. Extract audio via ffmpeg-python
#     audio_path = os.path.join(audio_dir, f"{base_name}.wav")
#     logger.info(f"Extracting audio to {audio_path} using ffmpeg-python...")
#     try:
#         (ffmpeg
#             .input(video_path)
#             .output(audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000')
#             .overwrite_output()
#             .run(capture_stdout=True, capture_stderr=True))
#         logger.info("Audio extraction complete.")
#     except ffmpeg.Error as e:
#         logger.error(f"ffmpeg-python extraction error: {e.stderr.decode()}")
#         raise

#     # Verify file exists
#     if not os.path.exists(audio_path):
#         error_msg = f"Audio file not found at {audio_path} after ffmpeg extraction."
#         logger.error(error_msg)
#         raise FileNotFoundError(error_msg)

#     # 2. Transcribe locally with Whisper
#     if MODEL is None:
#         raise RuntimeError("Whisper model is not loaded.")
#     logger.info(f"Transcribing audio {audio_path}...")
#     try:
#         result = MODEL.transcribe(audio_path)
#         logger.info("Transcription complete.")
#     except Exception as e:
#         logger.error(f"Transcription failed: {e}")
#         raise

#     # 3. Save transcript JSON
#     transcript_path = os.path.join(transcript_dir, f"{base_name}.json")
#     try:
#         with open(transcript_path, 'w') as f:
#             json.dump(result, f, indent=2)
#         logger.info(f"Transcript saved to {transcript_path}.")
#     except Exception as e:
#         logger.error(f"Failed to save transcript JSON: {e}")
#         raise

#     return audio_path, transcript_path
