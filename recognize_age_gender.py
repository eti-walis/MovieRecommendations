# Import required modules
import cv2 as cv
import math
import time
import argparse
import pathlib

#import os
#from picamera import PiCamera
#import picamera.array
#



from time import sleep

#import picamera
import time
import cv2

def take_a_picture():
    cap = cv.VideoCapture(0)
    path = pathlib.Path().resolve()
    # Capture frame
    ret, frame = cap.read()
    path_image = str(path) + "\\image.jpg"
    if ret:
        cv.imwrite(path_image, frame)
        # cv2.imshow('image',frame)
    cv2.waitKey(0)


    cap.release()
    return path_image

def getFaceBox(net, frame, conf_threshold=0.7):
    frameOpencvDnn = frame.copy()
    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]
    blob = cv.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])
            cv.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
    return frameOpencvDnn, bboxes ,frame

def get_data_from_face(image):
    parser = argparse.ArgumentParser(description='Use this script to run age and gender recognition using OpenCV.')
    parser.add_argument('--input',default=r"C:\Users\User\PycharmProjects\raspberrypi\3.jpeg" ,help='Path to input image or video file. Skip this argument to capture frames from a camera.')
    parser.add_argument("--device", default="cpu", help="Device to inference on")

    args = parser.parse_args()


    args = parser.parse_args()

    faceProto = "opencv_face_detector.pbtxt"
    faceModel = "opencv_face_detector_uint8.pb"

    ageProto = "age_deploy.prototxt"
    ageModel = "age_net.caffemodel"

    genderProto = "gender_deploy.prototxt"
    genderModel = "gender_net.caffemodel"

    MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
    ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
    genderList = ['Male', 'Female']

    # Load network
    ageNet = cv.dnn.readNet(ageModel, ageProto)
    genderNet = cv.dnn.readNet(genderModel, genderProto)
    faceNet = cv.dnn.readNet(faceModel, faceProto)


    if args.device == "cpu":
        ageNet.setPreferableBackend(cv.dnn.DNN_TARGET_CPU)

        genderNet.setPreferableBackend(cv.dnn.DNN_TARGET_CPU)

        faceNet.setPreferableBackend(cv.dnn.DNN_TARGET_CPU)

        print("Using CPU device")
    elif args.device == "gpu":
        ageNet.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        ageNet.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)

        genderNet.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        genderNet.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)

        genderNet.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        genderNet.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
        print("Using GPU device")

    print(args)
    # Open a video file or an image file or a camera stream
    cap = cv.VideoCapture(args.input if args.input else 0)
    #videoSourceIndex = 1
    #cap = cv.VideoCapture(cv.CAP_DSHOW + videoSourceIndex)

    padding = 20
    while cv.waitKey(1) < 0:
        # Read frame
        t = time.time()
        hasFrame, frame = cap.read()
        if not hasFrame:
            cv.waitKey()
            break

        frameFace, bboxes ,frame= getFaceBox(faceNet, frame)

        if not bboxes:
            print("No face Detected")
            return None, None, None

        for bbox in bboxes:
            # print(bbox)
            face = frame[max(0,bbox[1]-padding):min(bbox[3]+padding,frame.shape[0]-1),max(0,bbox[0]-padding):min(bbox[2]+padding, frame.shape[1]-1)]

            blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
            genderNet.setInput(blob)
            genderPreds = genderNet.forward()
            gender = genderList[genderPreds[0].argmax()]
            # print("Gender Output : {}".format(genderPreds))
            print("Gender : {}, conf = {:.3f}".format(gender, genderPreds[0].max()))

            ageNet.setInput(blob)
            agePreds = ageNet.forward()
            age = ageList[agePreds[0].argmax()]
            print("Age Output : {}".format(agePreds))
            print("Age : {}, conf = {:.3f}".format(age, agePreds[0].max()))

            label = "{},{}".format(gender, age)
            cv.putText(frameFace, label, (bbox[0], bbox[1]-10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv.LINE_AA)

            # cv.imshow("Age Gender Demo", frameFace)

            cv.imwrite('savedImage.jpg',frameFace)
            #cv.imwrite("age-gender-out-{}".format(args.input),frameFace)
        print("time : {:.3f}".format(time.time() - t))
    print(age.replace('(','').replace(')',''))

    path = pathlib.Path().resolve()
    path_image = str(path) + "\\savedImage.jpg"
    return age.replace('(','').replace(')',''), gender, path_image






"""# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = picamera.PiRGBArray(camera)
# allow the camera to warmup
time.sleep(2)
# grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array
# display the image on screen and wait for a keypress
cv2.imshow("Image", image)
cv2.waitKey(0)



"""
