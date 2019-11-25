#!/usr/bin/env python3

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
import subprocess
import os
from pydarknet import Detector, Image
import cv2

# A list of objects that we want to generally ignore
# (actual interesting ones are things like person, bear, dog, etc.)
# TODO consider adding "car" to the list
ObjectsToIgnore = ["bench", "chair", "sports ball"]

MARKER="Objects Detected"


#LABELS = open("/src/darknet/data/coco.names").read().strip().split("\n")
np.random.seed(42)
#COLORS = np.random.randint(0,255, size=(len(LABELS), 3), dtype="uint8")

#net = cv2.dnn.readNetFromDarknet("/src/darknet/cfg/yolov3.cfg", "/yolo/yolov3.weights")
#net = Detector(bytes("/src/darknet/cfg/yolov3.cfg", encoding="utf-8"),
#               bytes("/yolo/yolov3.weights", encoding="utf-8"), 0,
#               bytes("/src/darknet/cfg/coco.data", encoding="utf-8"))
net = Detector(bytes("cfg/yolov3.cfg", encoding="utf-8"),
               bytes("weights/yolov3.weights", encoding="utf-8"), 0,
               bytes("cfg/coco.data", encoding="utf-8"))


# This doesn't work to force GPU
#net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL)



# TODO this doesn't seem to work...
#net = cv2.dnn.readNetFromDarknet("./darknet/cfg/tiny.cfg", "./tiny.weights")

# GUI
#cv2.namedWindow("Processing...")

exitCode = 1
frameCount = 0
start = time.time()

for thumb in glob.glob(sys.argv[1] + "/**/*.thumb", recursive=True):
    filename = thumb[:len(thumb)-6]

    # First check to see if the thumbprint has the metadata we're expecting
    try:
        output = subprocess.check_output("identify -format '%c\n' "+thumb,
            shell=True)
        if MARKER in str(output):
            print("Skipping "+filename+" which already has been scanned: "+ str(output))
            continue
    except:
        print("WARNING: failed to read existing metadata on "+thumb)

    print("Processing " + filename)


    cap = cv2.VideoCapture(filename)

    bestMatches = {}
    if cap.isOpened(): # try to get the first img
        rval, img = cap.read()
    else:
        rval = False

    while rval:
        # TODO - consider optimization that breaks early if we have good object
        #        matches that are not in the ignore list so we can avoid wasting
        #        time processing all the rest of the frames
        frameCount += 1
        (H, W) = img.shape[:2]

        dark_frame = Image(img)
        results = net.detect(dark_frame)
        del dark_frame

        for cat, score, bounds in results:
            #print(cat, score, bounds)
            #x, y, w, h = bounds
            #cv2.rectangle(frame, (int(x-w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(255,0,0))
            #cv2.putText(frame, str(cat.decode("utf-8")), (int(x), int(y)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))
            label = str(cat.decode("utf-8"))
            if score > 0.9:
                if label not in bestMatches.keys() or float(bestMatches[label]) < float(score):
                    # TODO - find some way to weight based on number of frames
                    # e.g., a single frame with some random thing (suitcase, firehydant) is probably a misdetection
                    bestMatches[label] = float(score)

        # get next img
        rval, img = cap.read()

        # Filter out any objects we want to ignore
        for ignore in ObjectsToIgnore:
            if ignore in bestMatches:
                print("ignoring "+ignore)
                del bestMatches[ignore]

        # Short circuit if we have matches so we don't process the entire stream
        # to speed things up
        # TODO make this tunable
        if len(bestMatches) > 0:
            break

    if len(bestMatches) > 0:
        print(bestMatches)
        # TODO - replace the exitCode logic as it's stale
        exitCode = 0
        output = subprocess.check_output(
            "convert -comment '"+MARKER+":"+str(bestMatches).replace("'",'\"')+"' "+thumb+" "+thumb,
            shell=True)
        print("Updated "+thumb+ " " + str(output))
    else:
        print("Removing " + filename + " with no objects detected")
        os.remove(filename)
        os.remove(thumb)

    cap.release()
    end = time.time()
    print("Running Average time per frame: "+ str((end - start)/frameCount))

    sys.stdout.flush()

    # Uncomment to debug and break out after a single file is processed
    #break

end = time.time()

# GUI
#cv2.destroyAllWindows()

if frameCount > 0:
    print("Average time per frame: "+ str((end - start)/frameCount))
# Sleep for a little while so we can restart always with a brief pause...
time.sleep(5)
sys.exit(exitCode)
