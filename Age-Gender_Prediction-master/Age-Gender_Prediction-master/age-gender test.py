import cv2
import math
import numpy as np
import urllib.request

# Load pre-trained models
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
age_net = cv2.dnn.readNetFromCaffe('deploy_age.prototxt', 'age_net.caffemodel')
gender_net = cv2.dnn.readNetFromCaffe('deploy_gender.prototxt', 'gender_net.caffemodel')

# Define age and gender labels
age_labels = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
gender_labels = ['Male', 'Female']

# Open video capture (change 0 to video file path if reading from a file)
cap = cv2.VideoCapture(0)

while True:
    # Read frame from video
    ret, frame = cap.read()
    
    # Convert frame to gray scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    
    # Process each detected face
    for (x, y, w, h) in faces:
        # Extract face region of interest (ROI)
        face_roi = frame[y:y+h, x:x+w]
        
        # Preprocess face ROI for age and gender estimation
        blob = cv2.dnn.blobFromImage(face_roi, 1, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
        
        # Predict gender
        gender_net.setInput(blob)
        gender_preds = gender_net.forward()
        gender_idx = np.argmax(gender_preds)
        gender = gender_labels[gender_idx]
        
        # Predict age
        age_net.setInput(blob)
        age_preds = age_net.forward()
        age_idx = np.argmax(age_preds)
        age = age_labels[age_idx]
        
        # Draw bounding box and labels on the frame
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        label = f'{gender}, {age}'
        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv2.LINE_AA)
    
    # Display the resulting frame
    cv2.imshow('Age and Gender Estimation', frame)
    
    # Check for 'q' key press to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close windows
cap.release()
cv2.destroyAllWindows()
