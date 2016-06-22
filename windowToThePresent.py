#Anyone can use and abuse this code for any purpose. I have cited borrowed bits of code inline or in the readme file

import numpy as np
import cv2
import random
import csv
import os, os.path

previousVid = 0
#gets dir(ectory)Count from countVideos(), picks a random number between 1 and #of vids, grabs that video, 
#returns new video filename
def pickNewVid(dirCount):
    currentVid = random.randint(1,dirCount)

    #preventing the same video from playing twice in a row
    #This means you must start with TWO videos in the 'vids' folder or the program will crash
    global previousVid
    while currentVid == previousVid:
        #keep picking random numbbers until it's not the same as the last one
        currentVid = random.randint(1,dirCount)
        print "Guessing new number"
    previousVid = currentVid


    global vidString
    temp ='vid'+str(currentVid)+'.avi'
    vidString = os.path.join('...refactor3/vids', temp)
    return vidString

#just grabs a random quote out of the csv and removes all brackets and stuff
#returns clean quote
def getQuotes():
     with open('quotes.csv', 'rU') as datafile:
        allLines = list(datafile)
        global currentQuote
        currentQuote = allLines[random.randint(1,7)].strip()
        return currentQuote

#string counter
#from Stack Overlow user Gurney Alex: http://stackoverflow.com/questions/2657693/insert-a-newline-character-every-64-characters-using-python
def insert_newlines(string, every=10):
    lines = []
    global currentQuote
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
        currentQuote = '\n'.join(lines)
    return currentQuote

#Looks at the video folder and counts the files
#returns the count
def countVideos():
    dirname = r"...refactor3\vids"
    dirList = os.listdir(dirname)
    dirCount = len(dirList)
    return dirCount

#gets the number of files from countVideos(), puts the next sequential number into a file name, tacks that onto a path to the right folder
#Returns a new filename/path for videos being written
newNumber = 0
def getNewFilename(dirCount):
    global newNumber
    newNumber = dirCount+1
    newFilename = "vid"+str(newNumber)+".avi"
    newPath = os.path.join('...refactor3/vids', newFilename)
    print newFilename
    return newPath

#face detection
#returns viewer
frameCounter = 0
negCounter = 0
viewer = False
def checkViewer(viewer_frame):
    global frameCounter
    global negCounter
    global viewer

    #grayScale to help face detector
    gray = cv2.cvtColor(viewer_frame, cv2.COLOR_BGR2GRAY)
    #resizeCam = cv2.resize(gray, None, fx=0.5, fy=0.5, interpolation = cv2.INTER_AREA)

    #faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100,100),
            #flags = cv2.cv.CV_HAAR_SCALE_IMAGE
        )
    print "found {0} faces!".format(len(faces))


    #uncomment if you want rects around faces
    # for (x,y,w,h) in faces:
    #     cv2.rectangle(viewer_frame,(x,y),(x+w,y+h),(255,0,0),2)
    #     roi_gray = gray[y:y+h, x:x+w]
    #     roi_color = viewer_frame[y:y+h, x:x+w]


    #if you see a face, start counting frames. 
    if(len(faces)>0):
        frameCounter = frameCounter+1
        #if you see a face for ten frames in a row, then that counts as a viewer
        if(frameCounter>5):
            viewer = True
    #if you DON'T see  face, start counting frames
    else:
        negCounter = negCounter+1
        #if you don't see a face for five frames in a row, reset
        if negCounter>5:
            negCounter = 0
            frameCounter = 0
            viewer = False

    return viewer

#setting up face detection resources
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#initializng the video player
video_player= cv2.VideoCapture(pickNewVid(countVideos()))
#getQuotes()
#insert_newlines(currentQuote, every=10)

#initializing camera and codec
#Argument "1" is generally an attached webcam. On a laptop, "0" should be the built in camera
camera_capture = cv2.VideoCapture(1)
#codecs are not something I'm terribly familiar with, this took some experimenting
fourcc = cv2.VideoWriter_fourcc(*'XVID')

#setting globals for later use
viewer = False
viewCheckTimer = 0
frames = 0

font = cv2.FONT_HERSHEY_SIMPLEX

#outputPath = 'refactor3/vids/output.avi'
video_writer = cv2.VideoWriter()


############################
#MAIN LOOP
############################
#runForever
while(True):

    global viewer

    ret, next_frame = video_player.read()

    #if you don't see a video, go get a new one
    if (ret is False):
        video_player= cv2.VideoCapture(pickNewVid(countVideos()))
    #if you do have a video, play the next frame
    elif (ret):
        #Various adjustments to video that I used for testing, different looks, adding text, etc. 
        #gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)
        #texted = cv2.putText(next_frame, currentQuote, (100, 300), font, 1, (255,255,255), 2)
        resizer = cv2.resize(next_frame, (1024,768), interpolation = cv2.INTER_CUBIC)
        cv2.imshow('Framesies', resizer)

    #setting up the camera, which will be on throughout the program
    #un-comment second line to get a second window with camera view
    ret2, viewer_frame = camera_capture.read()
    cv2.imshow('camera_frame', viewer_frame)

    #for testing
    #print(video_writer.isOpened())

    #only check for viewer every 10 frames to speed things up
    viewCheckTimer = viewCheckTimer+1
    if viewCheckTimer == 10:
        #after ten frames, check
        viewer = checkViewer(viewer_frame)
        #if the viewer has gone away then reset frames, getting ready for a new viewer
        if not viewer:
            frames = 0
        viewCheckTimer = 0
    #print viewer

    ##########   
    #This is where we're actually going to write some video to file\
    #############
    #Counting frames to only record videos of a certain length
    #simple "timer" - 350 frames is about 10 seconds
    if frames<100:
        frames = frames + 1
        if viewer and ret2:
            if(video_writer.isOpened()):
                video_writer.write(viewer_frame)
                print "recording..."
            else:
                video_writer = cv2.VideoWriter(getNewFilename(countVideos()),fourcc, 30.0, (640, 480))

    #print frames to file
    else:
        print "we just chilling folk"
        if(video_writer.isOpened()):
            video_writer.release()


    #Program quitter - hit q to quit the program
    button = cv2.waitKey(1)
    #press "Q" to quit
    if button == ord('q'):
        break
        
camera_capture.release()
video_writer.release()
video_player.release()
cv2.destroyAllWindows()
    

