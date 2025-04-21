import os
import json
import logging
import numpy as np
import librosa
import cohere

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize Cohere client (expects COHERE_API_KEY in env)
COHERE_API_KEY = os.environ.get("COHERE_API_KEY", "O34WBadHOatc1tlLhoHnkLNx8Ov2nfU0MOgaa1Sy")
if not COHERE_API_KEY:
    logger.error("COHERE_API_KEY not set in environment.")
co = cohere.Client(COHERE_API_KEY)


def analyze_audio(audio_path: str) -> dict:
    """
    Extract prosodic features from an audio file:
      - RMS energy
      - Pitch (f0) via PYIN
      - Speaking rate (onset times)
    Returns a dict of lists.
    """
    y, sr = librosa.load(audio_path, sr=16000)
    frame_len = int(0.025 * sr)
    hop_len = int(0.010 * sr)

    rms = librosa.feature.rms(y=y, frame_length=frame_len, hop_length=hop_len)[0]
    f0, voiced_flag, voiced_prob = librosa.pyin(
        y,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        frame_length=frame_len,
        hop_length=hop_len
    )
    onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_len)
    onset_times = librosa.frames_to_time(onsets, sr=sr, hop_length=hop_len)

    return {
        'rms': rms.tolist(),
        'pitch': [float(x) if not np.isnan(x) else None for x in f0],
        'voiced_flag': voiced_flag.tolist(),
        'voiced_prob': voiced_prob.tolist(),
        'onset_times': onset_times.tolist()
    }


def load_transcript(transcript_path: str) -> list:
    """
    Load Whisper JSON transcript and return list of segments:
      each segment: {'start': float, 'end': float, 'text': str}
    """
    with open(transcript_path, 'r') as f:
        data = json.load(f)
    return [{'start': seg['start'], 'end': seg['end'], 'text': seg['text']} for seg in data.get('segments', [])]


def cohere_process_feedback(segments: list, audio_features: dict) -> str:
    """
    Send combined transcript segments and audio features to Cohere for comprehensive feedback.
    Returns the generated feedback text.
    """
    # Build prompt
    prompt = (
        "You are an expert interviewer and speech analyst. "
        "Evaluate the candidate's response based on:\n"
        "1. Answer correctness and relevance.\n"
        "2. Prosodic features (tone, energy, pitch, pacing).\n"
        "Provide feedback for each category.\n\n"
        "Transcript Segments:\n"
    )
    for seg in segments:
        prompt += f"[{seg['start']:.2f}-{seg['end']:.2f}] {seg['text']}\n"
    prompt += "\nAudio Features Summary:\n"
    # Summary stats
    rms_vals = np.array(audio_features['rms'])
    pitch_vals = np.array([p for p in audio_features['pitch'] if p is not None])
    rate = len(audio_features['onset_times']) / (len(rms_vals) * (10/1000))
    prompt += f"- Mean RMS energy: {rms_vals.mean():.3f}\n"
    prompt += f"- Median pitch: {np.median(pitch_vals):.1f} Hz\n"
    prompt += f"- Speaking rate: {rate:.2f} onsets/sec\n"

    # Call Cohere
    response = co.generate(
        prompt=prompt,
        model='command',
        max_tokens=300,
        temperature=0.7
    )
    return response.generations[0].text.strip()


def save_feedback(feedback: dict, out_dir: str = 'feedback') -> str:
    """
    Save the feedback dict as JSON in out_dir. Returns the file path.
    """
    os.makedirs(out_dir, exist_ok=True)
    base = feedback.get('video', 'output')
    out_path = os.path.join(out_dir, f"{base}_feedback.json")
    with open(out_path, 'w') as f:
        json.dump(feedback, f, indent=2)
    logger.info(f"Feedback saved to {out_path}")
    return out_path
