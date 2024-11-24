from django.shortcuts import redirect, render, get_object_or_404
from django.http import StreamingHttpResponse, JsonResponse
from .models import Presentation, Feedback
from .forms import PresentationForm
import cv2
import mediapipe as mp
import speech_recognition as sr#volume and pace
import moviepy.editor as mp_editor
import audioop
import numpy as np
from keras.models import load_model  # type: ignore
import threading

# Load the pre-trained emotion detection model
emotion_model = load_model('presentations/models/model.h5')
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)

labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}
def Home_page(request):
    return render(request,'presentations/header.html')

def upload_presentation(request):
    if request.method == 'POST':
        form = PresentationForm(request.POST, request.FILES)
        if form.is_valid():
            presentation = form.save()
            # Start the video processing in a separate thread
            thread = threading.Thread(target=process_video_and_save_feedback, args=(presentation.video.path, presentation))
            thread.start()
            # Redirect to video feed page with the new video's ID
            return redirect('video_feed_page', video_id=presentation.id)
    else:
        form = PresentationForm()
    return render(request, 'presentations/upload.html', {'form': form})
def video_feed_page(request, video_id):
    return render(request, 'presentations/video_feed.html', {'video_id': video_id})

def video_feed(request, video_id):
    presentation = get_object_or_404(Presentation, id=video_id)
    video_path = presentation.video.path

    def generate():
        cap = cv2.VideoCapture(video_path)
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Annotate the frame with gesture and posture data
            annotated_frame = annotate_frame(frame, pose)

            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        cap.release()

    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

def annotate_frame(frame, pose):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    
    if results.pose_landmarks:
        key_points = [{'x': lm.x, 'y': lm.y, 'z': lm.z} for lm in results.pose_landmarks.landmark]
        
        # Draw gestures
        for lm in results.pose_landmarks.landmark:
            x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        # Draw posture lines
        left_shoulder = key_points[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = key_points[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = key_points[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        right_hip = key_points[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]
        #line he posture sathi ahe
        cv2.line(frame, (int(left_shoulder['x'] * frame.shape[1]), int(left_shoulder['y'] * frame.shape[0])),
                 (int(right_shoulder['x'] * frame.shape[1]), int(right_shoulder['y'] * frame.shape[0])), (255, 0, 0), 2)
        cv2.line(frame, (int(left_hip['x'] * frame.shape[1]), int(left_hip['y'] * frame.shape[0])),
                 (int(right_hip['x'] * frame.shape[1]), int(right_hip['y'] * frame.shape[0])), (255, 0, 0), 2)

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
    for (x, y, w, h) in faces:
        face = gray_frame[y:y+h, x:x+w]
        face = cv2.resize(face, (48, 48))
        img = extract_features(face)
        pred = emotion_model.predict(img)
        emotion_label = labels[pred.argmax()]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, emotion_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)#bgr

    return frame

def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0

def process_video_and_save_feedback(video_path, presentation):
    video_feedback = process_video(video_path)
    audio_feedback = process_audio(video_path)

    gesture_score = score_gestures(video_feedback['gestures'])
    posture_score = score_posture(video_feedback['posture'])
    volume_score = score_volume_refined(audio_feedback['volume'])
    pace_score = score_pace(audio_feedback['pace'])
    emotion_score = score_emotions(video_feedback['expressions'])

    overall_score = (gesture_score + posture_score + volume_score + pace_score + emotion_score) / 5

    feedback_record, created = Feedback.objects.get_or_create(presentation=presentation)
    feedback_record.gesture_score = gesture_score
    feedback_record.posture_score = posture_score
    feedback_record.volume_score = volume_score
    feedback_record.pace_score = pace_score
    feedback_record.emotion_score = emotion_score
    feedback_record.overall_score = overall_score
    feedback_record.processing_complete = True
    feedback_record.save()
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    feedback = {
        "gestures": [],
        "posture": [],
        "expressions": []
    }
    frame_count = 0  # Counter to keep track of frame number
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Process only every 5th frame
        if frame_count % 10 == 0:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            if results.pose_landmarks:
                key_points = [{'x': lm.x, 'y': lm.y, 'z': lm.z} for lm in results.pose_landmarks.landmark]
                feedback['gestures'].append(key_points)
                feedback['posture'].append(key_points)  # Collecting posture data as well

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
            for (x, y, w, h) in faces:
                face = gray_frame[y:y+h, x:x+w]
                face = cv2.resize(face, (48, 48))
                img = extract_features(face)
                pred = emotion_model.predict(img)
                emotion_label = labels[pred.argmax()]
                feedback['expressions'].append(emotion_label)

    cap.release()
    return feedback


def process_audio(video_path):
    video_clip = mp_editor.VideoFileClip(video_path)
    audio_path = video_path.replace('.mp4', '.wav')
    video_clip.audio.write_audiofile(audio_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        audio_frame_data = audio_data.get_wav_data()  # Correct method to get WAV data
    
    transcription = recognizer.recognize_google(audio_data)
    
    feedback = {
        "transcription": transcription,
        "volume": analyze_volume(audio_frame_data),
        "pace": analyze_pace(transcription)
    }
    return feedback


def analyze_volume(audio_data):
    # 'audio_data' is already a bytes object, so we pass it directly to audioop.rms
    rms = audioop.rms(audio_data, 2)
    
    # Define volume categories
    ideal_min_volume = 500
    ideal_max_volume = 2000

    if rms < ideal_min_volume:
        volume_category = "Too quiet"
    elif rms > ideal_max_volume:
        volume_category = "Too loud"
    else:
        volume_category = "Normal"
    
    return volume_category

def process_audio(video_path):
    video_clip = mp_editor.VideoFileClip(video_path)
    audio_path = video_path.replace('.mp4', '.wav')
    video_clip.audio.write_audiofile(audio_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        audio_frame_data = audio_data.get_wav_data()  # Correct method to get WAV data
    
    transcription = recognizer.recognize_google(audio_data)
    
    feedback = {
        "transcription": transcription,
        "volume": analyze_volume(audio_frame_data),  # Pass the bytes object directly
        "pace": analyze_pace(transcription)
    }
    return feedback

def analyze_pace(text):
    words = text.split()
    duration = len(text) / 60  # Assuming length of text as duration in seconds
    pace = len(words) / duration if duration > 0 else 0
    return pace


def score_gestures(gestures):
    total_frames = len(gestures)
    score = 0
    
    for frame_index, frame in enumerate(gestures):
        left_shoulder = frame[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = frame[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_elbow = frame[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        right_elbow = frame[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value]
        left_wrist = frame[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = frame[mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value]
        

        # Scoring without visibility check
        if left_shoulder['y'] < left_elbow['y']:
            score += 1
        if right_shoulder['y'] < right_elbow['y']:
            score += 1
        if left_elbow['y'] < left_wrist['y']:
            score += 1
        if right_elbow['y'] < right_wrist['y']:
            score += 1
    
    max_score = total_frames * 4  # Adjust based on your scoring criteria
    percentage = (score / max_score) * 100 if max_score > 0 else 0
    return percentage


def score_posture(posture_data):
    total_frames = len(posture_data)
    correct_posture_frames = 0

    for frame in posture_data:
        left_shoulder = frame[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = frame[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = frame[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        right_hip = frame[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]
        left_knee = frame[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        right_knee = frame[mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value]
        nose = frame[mp.solutions.pose.PoseLandmark.NOSE.value]

        # Ensure shoulders are level
        shoulders_level = abs(left_shoulder['y'] - right_shoulder['y']) < 0.05
        
        # Ensure hips are level
        hips_level = abs(left_hip['y'] - right_hip['y']) < 0.05
        
        # Ensure head is above shoulders
        head_above_shoulders = nose['y'] < min(left_shoulder['y'], right_shoulder['y'])
        
        # Ensure shoulders and hips are vertically aligned
        shoulders_hips_aligned = abs((left_shoulder['x'] + right_shoulder['x']) / 2 - (left_hip['x'] + right_hip['x']) / 2) < 0.1
        
        # Ensure the spine is straight (shoulders to hips alignment)
        spine_straight = abs(left_shoulder['x'] - left_hip['x']) < 0.1 and abs(right_shoulder['x'] - right_hip['x']) < 0.1
        
        # Ensure knees are aligned with hips
        knees_aligned = abs(left_knee['x'] - left_hip['x']) < 0.1 and abs(right_knee['x'] - right_hip['x']) < 0.1
        
        if shoulders_level and hips_level and head_above_shoulders and shoulders_hips_aligned and spine_straight and knees_aligned:
            correct_posture_frames += 1

    percentage = (correct_posture_frames / total_frames) * 100 if total_frames > 0 else 0
    return percentage


def score_volume_refined(audio_data):
    if isinstance(audio_data, str):
        # Convert string to bytes
        audio_data = audio_data.encode('latin1')
    elif not isinstance(audio_data, (bytes, bytearray)):
        raise TypeError("Expected a bytes-like object, not {}".format(type(audio_data).__name__))
    
    rms = audioop.rms(audio_data, 2)
    
    # Define volume categories
    ideal_min_volume = 300
    ideal_max_volume = 1500
    
    if rms < ideal_min_volume:
        volume_category = "Too quiet"
        percentage = (rms / ideal_min_volume) * 50 if rms > 0 else 0  # Scaled score for quiet volume
    elif rms > ideal_max_volume:
        volume_category = "Too loud"
        # Use a different scaling factor to penalize loud volume less harshly
        percentage = 75 + (25 * (ideal_max_volume / rms)) if rms > 0 else 75
        if percentage > 100:
            percentage = 100
    else:
        volume_category = "Normal"
        percentage = 100
    
    return percentage

def score_pace(pace):
    ideal_pace = 110  # Ideal words per minute
    
    # Define boundaries for scoring
    boundaries = [
        (ideal_pace * 0.90, ideal_pace * 1.10, 100),  # 90% to 110% of ideal pace
        (ideal_pace * 0.80, ideal_pace * 1.20, 85),   # 80% to 120% of ideal pace
        (ideal_pace * 0.70, ideal_pace * 1.30, 70),   # 70% to 130% of ideal pace
        (ideal_pace * 0.60, ideal_pace * 1.40, 55),   # 60% to 140% of ideal pace
        (0, ideal_pace * 0.60, 40),                   # Below 60% of ideal pace
        (ideal_pace * 1.40, float('inf'), 40)         # Above 140% of ideal pace
    ]
    
    for lower_bound, upper_bound, score in boundaries:
        if lower_bound < pace <= upper_bound:
            return score
    return 0



def score_emotions(emotions):
    emotion_counts = {emotion: emotions.count(emotion) for emotion in set(emotions)}
    positive_emotions = emotion_counts.get('happy', 0) + emotion_counts.get('surprise', 0)
    neutral_emotions = emotion_counts.get('neutral', 0)
    negative_emotions = emotion_counts.get('angry', 0) + emotion_counts.get('disgust', 0) + emotion_counts.get('fear', 0) + emotion_counts.get('sad', 0)

    total_emotions = positive_emotions + neutral_emotions + negative_emotions
    if total_emotions == 0:
        return 0

    # Adjusting weightage to increase score
    emotion_score = (positive_emotions * 1.5 + neutral_emotions * 0.5) / total_emotions * 100
    return min(emotion_score, 100)  # Ensure the score does not exceed 100


def feedback_status(request, video_id):
    feedback = Feedback.objects.filter(presentation_id=video_id).first()
    if feedback:
        if feedback.processing_complete:
            return JsonResponse({'status': 'complete'})
    return JsonResponse({'status': 'processing'})
def feedback(request, video_id):
    feedback = get_object_or_404(Feedback, presentation_id=video_id)
    return render(request, 'presentations/feedback.html', {'feedback': feedback, 'video_id': video_id})
def overview_page(request,video_id):
    feedback = get_object_or_404(Feedback, presentation_id=video_id)
    return render(request,'presentations/overview.html',{'feedback': feedback, 'video_id': video_id})