import numpy as np
import cv2
print(cv2.__file__)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_bollard.xml')

cap = cv2.VideoCapture(0)
img_counter = 0

while(True):
    # Each frame
    ret, frame = cap.read()

    

    # Convert to gray scale for it to work
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Change scaleFactor for highest accuracy (1.5, 5) is documentation
    faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.5, minNeighbors = 5)

    for (x, y, w, h) in faces:
        print(x, y, w, h)
        # rate of interest around my face
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        color = (0, 0, 255) # BGR btw
        stroke = 2 # Thickeness
        cv2.rectangle(frame, (x,y), (x+w, y+h), color, stroke) # Draw Rectangle


    # Display frame
    cv2.imshow('frame', frame)
    #key = cv2.waitKey(5000)
    #print(key)
    if cv2.waitKey(20) & 0xFF == ord('a'):
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
        

#Destroy everything after finished
cap.release()
cv2.destroyAllWindows()
