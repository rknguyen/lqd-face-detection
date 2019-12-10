from threading import Thread
from queue import Queue

import requests
import copy
import cv2
import pcn
import base64


def rescale_frame(frame, percent=75):
    scale_percent = percent
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)


def face_detection():
    cam = cv2.VideoCapture(0)
    global preFaceCount
    while cam.isOpened():
        ret, img = cam.read()
        img = rescale_frame(img, percent=35)
        clone_img = copy.copy(img)

        winlist = pcn.detect(img)
        drawed_img = pcn.draw(img, winlist)

        cv2.imshow('window', img)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            face = winlist[0]
            x1 = face.x
            y1 = face.y
            x2 = face.width + face.x - 1
            y2 = face.width + face.y - 1
            aligned_image = clone_img[y1:y2, x1:x2]

            retval, buffer = cv2.imencode('.jpg', aligned_image)
            jpg_as_text = base64.b64encode(buffer)
            data = {"image": jpg_as_text, "user_id": username}
            r = requests.post(
                url="http://68.183.226.196:1210/register", data=data)
            if (r == "OK"):
                print("OK")
            break


if __name__ == "__main__":
    cv2.namedWindow('window')

    username = input("Username: ")

    face_detection()
