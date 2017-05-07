#########################################################
#
#   SecurFace.py
# 
#          Run : python SecurFace.py
#   Written by : Austin Kothig
#     Semester : SPRING 2017
#      Purpose : Given input from a webcam, if a
#                face has been detected, send a
#                screen shot of that face over
#                facebook to some person
# 
#########################################################

import cv2
import time
import fbchat

def detect(img, cascade):
    rects = cascade.detectMultiScale(img,
                                     scaleFactor = 1.3,
                                     minNeighbors = 4,
                                     minSize = (30, 30),
                                     flags = cv2.CASCADE_SCALE_IMAGE)
    # no Faces found
    if len(rects) == 0:
        return []

    # faces found
    rects[:,2:] += rects[:,:2]
    global DETECTED
    DETECTED = True
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

if __name__ == '__main__':

    # Define bool variables for when
    # a photo should be saved
    global DETECTED
    DETECTED = False

    # Define Log in information
    # and the user to send faces to
    USERNAME = "[YOUR EMAIL ADDRESS]"
    PASSWORD = "[YOUR PASSWORD]"
    SENDTO   = "[YOUR DESTINATION USER]"

    # Log into facebook
    client = fbchat.Client(USERNAME, PASSWORD)
    friends = client.getUsers(SENDTO)
    friend = friends[0]

    # Used for photo indexing
    shot_idx = 0
    
    # Build the Cascades from Data
    cascade = cv2.CascadeClassifier("./xml/haarcascade_frontalface_default.xml")
    
    #Start the Capture
    cap = cv2.VideoCapture(0)

    while True:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        # detect faces
        rects = detect(gray, cascade)
        vis = img.copy()
        draw_rects(vis, rects, (0, 255, 0))

        print DETECTED, time.time()%5

        if DETECTED:
            fn = './Capture/shot_%03d.bmp' % (shot_idx)
            cv2.imwrite(fn, img)
            print fn, 'saved'
            client.sendLocalImage(friend.uid,message='',image=fn)
            shot_idx += 1 # increase the capture index
            time.sleep(3) # sleep for 3 seconds
           
        DETECTED = False      

        cv2.imshow('facedetect', vis)
        
        if cv2.waitKey(5) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
