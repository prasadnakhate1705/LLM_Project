import cv2
import mediapipe as mp
import time
from datetime import datetime
from json_utils import load_sessions, save_sessions, remove_old_sessions

mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose

class InterviewAnalytics:
    def __init__(self):
        self.session_start_time = time.time()
        self.eye_contact_duration = 0
        self.last_eye_contact_time = None
        self.hand_gesture_counts = {
            "open_palm": 0,
            "closed_fist": 0,
            "pointing": 0,
            "hand_near_face": 0,
            "excessive_movement": 0,
            "neutral": 0,
            "thumbs_up": 0
        }
        self.poor_posture_duration = 0
        self.last_poor_posture_time = None

    def update_eye_contact(self, has_contact):
        current_time = time.time()
        if has_contact:
            if self.last_eye_contact_time is not None:
                self.eye_contact_duration += (current_time - self.last_eye_contact_time)
            self.last_eye_contact_time = current_time
        else:
            self.last_eye_contact_time = None

    def update_gesture(self, gesture_type):
        if gesture_type in self.hand_gesture_counts:
            self.hand_gesture_counts[gesture_type] += 1

    def update_posture(self, is_good_posture):
        current_time = time.time()
        if not is_good_posture:
            if self.last_poor_posture_time is not None:
                self.poor_posture_duration += (current_time - self.last_poor_posture_time)
            self.last_poor_posture_time = current_time
        else:
            self.last_poor_posture_time = None

    def get_session_duration(self):
        return time.time() - self.session_start_time

    def get_eye_contact_percentage(self):
        duration = self.get_session_duration()
        return (self.eye_contact_duration / duration) * 100 if duration > 0 else 0

    def get_poor_posture_percentage(self):
        duration = self.get_session_duration()
        return (self.poor_posture_duration / duration) * 100 if duration > 0 else 0

    def get_dominant_gesture(self):
        return max(self.hand_gesture_counts, key=self.hand_gesture_counts.get)

class InterviewAnalyzer:
    def __init__(self):
        self.analytics = InterviewAnalytics()
        self.gesture_history = []
        self.eye_contact_history = []
        self.posture_history = []
        self.prev_hand_pos = None
        self.hands_model = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
        self.face_model = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)
        self.pose_model = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

    def analyze_frame(self, image):
        image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        hand_results = self.hands_model.process(image_rgb)
        face_results = self.face_model.process(image_rgb)
        pose_results = self.pose_model.process(image_rgb)

        # Hand gesture analysis (dummy example)
        if hand_results.multi_hand_landmarks:
            landmarks = hand_results.multi_hand_landmarks[0]
            self.analytics.update_gesture("open_palm")

        # Eye contact (dummy logic for example)
        if face_results.multi_face_landmarks:
            self.analytics.update_eye_contact(True)

        # Posture (dummy logic for example)
        if pose_results.pose_landmarks:
            self.analytics.update_posture(True)

    def generate_report(self):
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration": int(self.analytics.get_session_duration()),
            "eye_contact": int(self.analytics.get_eye_contact_percentage()),
            "posture": 100 - int(self.analytics.get_poor_posture_percentage()),
            "gestures": {g: c for g, c in self.analytics.hand_gesture_counts.items() if c > 0},
            "recommendations": self._generate_recommendations()
        }
        return report

    def _generate_recommendations(self):
        recs = []
        if self.analytics.get_eye_contact_percentage() < 60:
            recs.append("Improve eye contact")
        if self.analytics.get_poor_posture_percentage() > 30:
            recs.append("Maintain better posture")
        if self.analytics.hand_gesture_counts["hand_near_face"] > 5:
            recs.append("Avoid touching face during interviews")
        if self.analytics.hand_gesture_counts["excessive_movement"] > 10:
            recs.append("Reduce hand movement to show confidence")
        return recs

def coach_video_file(path):
    cap = cv2.VideoCapture(path)
    analyzer = InterviewAnalyzer()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        analyzer.analyze_frame(frame)

    cap.release()
    session_data = analyzer.generate_report()

    # Save to JSON with 5-year cleanup
    sessions = load_sessions()
    sessions.append(session_data)
    sessions = remove_old_sessions(sessions)
    save_sessions(sessions)

    return session_data
