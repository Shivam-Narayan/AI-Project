import os, pickle
import cv2
from imutils import paths
import streamlit as st
import tensorflow as tf
import numpy as np


def filter_genres(img_path):
    genre = ['Happy', 'Surprise']
    emotion_labels = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}
    frame = cv2.imread(img_path)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # model =  tf.keras.models.load_model('best_model.keras')
    with open('emotion_model1.pkl', 'rb') as file:
        model = pickle.load(file)

    for (x, y, w, h) in faces:
        # Extract the ROI (Region of Interest) containing the face
        roi_gray = gray[y:y+h, x:x+w]
        roi_gray = cv2.resize(roi_gray, (48, 48))
        
        # Preprocess the image for prediction
        roi = roi_gray.astype('float') / 255.0
        roi = tf.keras.preprocessing.image.img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        
        # Make predictions
        preds = model.predict(roi)[0]
        label = emotion_labels[preds.argmax()]

        return True if label in genre else False



def is_face_dominant(image, face_cascade,  min_face_area_ratio=0.02):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
    frame_height, frame_width = image.shape[:2]
    frame_area = frame_height * frame_width
    
    for (x, y, w, h) in faces:
        face_area = w * h
        face_area_ratio = face_area / frame_area
        
        if face_area_ratio >= min_face_area_ratio:
            return True
    
    return False

def filter_frames_with_dominant_face(input_folder, output_folder, cnn_model, video_type, min_face_area_ratio=0.005):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    flag = False
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cnt = 1
    lst = []
    # Create placeholders for displaying images
    placeholder_col1 = st.empty()
    placeholder_col2 = st.empty()
    placeholder_col3 = st.empty()
    for frame_path in sorted(paths.list_images(input_folder)):
        if cnt <= 5:
            cnt+=1
            continue
        frame = cv2.imread(frame_path)
        frame_name = os.path.basename(frame_path)

        scale_factor = 0.5  # Resize to 50% of the original size
        resized_image = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
        
        # Convert the resized image to RGB
        rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        
        # Detect faces using CNN face detector
        detections = cnn_model(rgb_image, 1)
        # lst.append(frame_path)

        # if len(lst) >= 3:
            
        #     with placeholder_col1:
        #             st.image(lst[-3], width=150)
        #     with placeholder_col2:
        #             st.image(lst[-2], width=150)
        #     with placeholder_col3:
        #             st.image(lst[-1], width=150)
            
            # Clear the list after displaying
        # lst = []
        # Check if any faces were detected
        if len(detections) > 0:
            pass
        else:
            continue
        
        if video_type == 'Others':
            if filter_genres(frame_path):
                if is_face_dominant(frame, face_cascade, min_face_area_ratio):
                    output_frame_path = os.path.join(output_folder, frame_name)
                    cv2.imwrite(output_frame_path, frame)
                    flag = True
                    lst.append(frame_path)
                    if len(lst) >= 3:
                        with placeholder_col1:
                                st.image(lst[-3], width=150)
                        with placeholder_col2:
                                st.image(lst[-2], width=150)
                        with placeholder_col3:
                                st.image(lst[-1], width=150)
                        
                        # Clear the list after displaying
                        lst = []
                    print(f"Saved frame with dominant face: {frame_name}")
                else:
                    print(f"Removed frame: {frame_name} - Face not dominant")
        else:
            if is_face_dominant(frame, face_cascade, min_face_area_ratio):
                output_frame_path = os.path.join(output_folder, frame_name)
                cv2.imwrite(output_frame_path, frame)
                flag = True
                lst.append(frame_path)
                if len(lst) >= 3:
                        with placeholder_col1:
                                st.image(lst[-3], width=150)
                        with placeholder_col2:
                                st.image(lst[-2], width=150)
                        with placeholder_col3:
                                st.image(lst[-1], width=150)
                        
                        # Clear the list after displaying
                        lst = []
                print(f"Saved frame with dominant face: {frame_name}")
            else:
                print(f"Removed frame: {frame_name} - Face not dominant")

    placeholder_col1.empty()
    placeholder_col2.empty()
    placeholder_col3.empty()
    return flag


# Example usage
# input_frames_dir = "downloads/frames"
# output_frames_dir = "downloads/filtered_faces"
# blur_threshold = 65
# filter_frames_with_dominant_face(input_frames_dir, output_frames_dir,  min_face_area_ratio=0.02)
