#########################################################
#
#   SecurFace.py
# 
#          Run : python SecurMove.py
#   Written by : Austin Kothig
#     Semester : SPRING 2017
#      Purpose : Given input from a webcam, if a
#                movement has been detected,
#                send a screen shot of that
#                over facebook to some person
# 
#########################################################

import cv2
import time
import fbchat
import numpy as np

def draw_flow(img, flow, step=16):
    global DETECTED
    global STATICMOVE
    
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1).astype(int)
    fx, fy = flow[y,x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))

    if (lines - STATICMOVE >= 10).any():
        DETECTED = True
    
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis


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
    
    # Start the Capture
    cap = cv2.VideoCapture(0)
    ret, prev = cap.read()
    prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    # Used for comparing movement
    prevflow = cv2.calcOpticalFlowFarneback(prevgray, prevgray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    step = 16
    h, w = prevgray.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1).astype(int)
    fx, fy = prevflow[y,x].T
    line = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    line = np.int32(line + 0.5)
    global STATICMOVE
    STATICMOVE = line

    while True:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        flow = cv2.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        prevgray = gray

        DETECTED = False
        
        cv2.imshow('movedetect', draw_flow(gray, flow))
        print DETECTED, time.time()%5       

        
        if DETECTED:
            fn = './Capture/shot_%03d.bmp' % (shot_idx)
            cv2.imwrite(fn, img)
            print fn, 'saved'
            client.sendLocalImage(friend.uid,message='',image=fn)
            shot_idx += 1 # increase the capture index
            time.sleep(5) # sleep for 5 seconds        
        
        if cv2.waitKey(5) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
