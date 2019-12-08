from threading import Thread
from queue import Queue

import copy
import cv2
import pcn
import base64
import requests


def do_work(image):
    try:
        retval, buffer = cv2.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer)
        data = {"image": jpg_as_text}
        r = requests.post(url="http://127.0.0.1:1210/recognize", data=data)
        print(r.text)
    except:
        pass


def worker():
    while True:
        item = q.get()
        do_work(item)
        q.task_done()


def rescale_frame(frame, percent=75):
    scale_percent = percent
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)


def face_detection():
    cam = cv2.VideoCapture(0)
    global preFaceCount
    preFaceCount = 0
    while cam.isOpened():
        ret, img = cam.read()
        img = rescale_frame(img, percent=35)

        clone_img = copy.copy(img)

        winlist = pcn.detect(img)
        curFaceCount = len(winlist)
        if (curFaceCount > preFaceCount):
            if (len(winlist) > 0):
                for win in winlist:
                    face = winlist[0]
                    x1 = face.x
                    y1 = face.y
                    x2 = face.width + face.x - 1
                    y2 = face.width + face.y - 1
                    aligned_image = clone_img[y1:y2, x1:x2]
                    q.put(aligned_image)

        drawed_img = pcn.draw(img, winlist)

        cv2.imshow('window', img)

        preFaceCount = curFaceCount
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    cv2.namedWindow('window')

    q = Queue()

    for x in range(8):
        t = Thread(target=worker)
        t.start()

    t2 = Thread(target=face_detection)
    t2.start()

    cv2.waitKey(0)
    cv2.destroyAllWindows()
