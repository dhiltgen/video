#!/usr/bin/env python2

#
# Really simple CV script to scan a video to see if any objects
# are detected.

# TODO set more tunables by env vars
#
# TODO Add a mode to replace the video with an overlaid version showing
#      bounding boxes and labels for troubleshooting

import cv2
import numpy as np
import glob
import time
import sys

DOWNSCALE=4


LABELS = open("/src/darknet/data/coco.names").read().strip().split("\n")
np.random.seed(42)
COLORS = np.random.randint(0,255, size=(len(LABELS), 3), dtype="uint8")

net = cv2.dnn.readNetFromDarknet("/src/darknet/cfg/yolov3.cfg", "/yolo/yolov3.weights")

# TODO this doesn't seem to work...
#net = cv2.dnn.readNetFromDarknet("./darknet/cfg/tiny.cfg", "./tiny.weights")

# GUI
#cv2.namedWindow("Processing...")

exitCode = 1
frameCount = 0
start = time.time()


for filename in sys.argv[1:]:
    print("Processing " + filename)
    cap = cv2.VideoCapture(filename)

    bestMatches = {}
    if cap.isOpened(): # try to get the first img
        rval, img = cap.read()
    else:
        rval = False

    while rval:
        frameCount += 1
        (H, W) = img.shape[:2]
        ln = net.getLayerNames()
        ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        blob = cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        layerOutputs = net.forward(ln)

        boxes = []
        confidences = []
        classIDs = []

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > 0.5:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width /2))
                    y = int(centerY - (height/ 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
                    if LABELS[classID] not in bestMatches.keys() or float(bestMatches[LABELS[classID]]) < float(confidence):
                        # TODO - find some way to weight based on number of frames
                        # e.g., a single frame with some random thing (suitcase, firehydant) is probably a misdetection
                        bestMatches[LABELS[classID]] = float(confidence)

        # TODO - clean up this section as a separate function that's only used in GUI mode
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)

        if len(idxs) > 0:
            for i in idxs.flatten():
                (x,y) = (boxes[i][0], boxes[i][1])
                (w,h) = (boxes[i][2], boxes[i][3])
                color = [int(c) for c in COLORS[classIDs[i]]]
                cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
                text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
                cv2.putText(img, text, (x,y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # GUI
        #cv2.imshow("preview", img)

        # get next img
        rval, img = cap.read()

        #key = cv2.waitKey(1)
        #if key in [27, ord('Q'), ord('q')]: # exit on ESC
        #    break

    if len(bestMatches) > 0:
        print(bestMatches)
        exitCode = 0
    cap.release()

end = time.time()

# GUI
#cv2.destroyAllWindows()

print("Average time per frame: "+ str((end - start)/frameCount))
sys.exit(exitCode)
