import numpy as np
import cv2
import random
import os.path

cap = cv2.VideoCapture(0)

# check the path to the classifier files, to avoid Assert !empty() error
if os.path.exists('/usr/share/opencv/haarcascades/'):
    # on pi 2 running raspbian
    face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_eye.xml')
elif os.path.exists('/usr/share/OpenCV/haarcascades/'):
    # on openSUSE Leap 42.2 using opencv 3.1
    face_cascade = cv2.CascadeClassifier('/usr/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('/usr/share/OpenCV/haarcascades/haarcascade_eye.xml')
else:
    print("Unknown path to classifier files, exiting")
    exit(1)


#original version that worked on Pi 2
#fourcc = cv2.cv.CV_FOURCC(*'MJPG')
# opensuse with opencv 3.1
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
# this resolution works fine with my MS LifeCam Cinema
out = cv2.VideoWriter('geeko-output.avi', fourcc, 20.0, (640,480))


while(cap.isOpened()):
    #img = cv2.imread('aurelien.jpg')
    #img = cv2.imread('face-jad.jpg')
    #img = cv2.imread('trump.jpg')
    #img = cv2.imread('face.jpg')  # lots of faces, just too small for eye detection alg
    
    ret, img = cap.read()
    if ret == True:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


        # image, scale factor, minneighbors
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        #faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            print("got one face")
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            #eyes = eye_cascade.detectMultiScale(roi_gray)
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.3, 5)
            for (ex,ey,ew,eh) in eyes:
                print("found an eye")
                # calc thicknesses
                thick = int(ew/10)
                if thick < 2:
                    thick = 2
                xmotion = random.randint(-2, 2)
                ymotion = random.randint(-2, 2)
     
                #cv2.circle(roi_color,(ex+ew/2,ey+eh/2), int(ew/1.8), (115,186,37), thick)
                cv2.circle(roi_color,(ex+ew/2,ey+eh/2), int(ew/1.7), (255,255,255), -1)
                cv2.circle(roi_color,(ex+ew/2,ey+eh/2), int(ew/1.6), (115,186,37), thick)
                # fixed size pupil
                cv2.circle(roi_color,(ex+ew/2 + thick * xmotion, ey+eh/2 + thick*ymotion ), 2 * thick, (115,186,37), -1)

        cv2.imshow('img',img)
        out.write(img)

        if cv2.waitKey(0) & 0xFF == ord('q'):
            break


cap.release()
out.release()
cv2.destroyAllWindows()
