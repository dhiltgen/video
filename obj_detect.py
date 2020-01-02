#!/usr/bin/env python3

#
# CV script to scan a video to see if any objects
# are detected.

# TODO set more tunables by env vars
threshold = 0.90
minFrames = 10
dryRun = False

#
# TODO Add a mode to replace the video with an overlaid version showing
#      bounding boxes and labels for troubleshooting

import cv2
#import numpy as np
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
ObjectsToIgnore = ["bench", "chair", "sports ball", "frisbee", "bed", "baseball bat", "bird", "diningtable", "fork", "boat"]

MARKER="Objects Detected"


#LABELS = open("/src/darknet/data/coco.names").read().strip().split("\n")
#np.random.seed(42)
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

frameCount = 0
start = time.time()

# Return true if there are suitable matches in the dict
def hasGoodObjects(matches):
    if len(matches) == 0:
        return False

    # Special case cars and trucks - only keep if there's some other objects (person, etc.)
    if len(matches) == 1 and ("car" in matches or "truck" in matches):
        return False

    # Always keep bears (also sometimes matched as cats)
    if "bear" in matches or "cat" in matches:
        return True

    for label in matches.keys():
        (score, count) = matches[label]
        if count > minFrames:
            return True
    return False


print("Processing videos from " + sys.argv[1])
for thumb in glob.glob(sys.argv[1] + "/**/*.thumb", recursive=True):
    filename = thumb[:len(thumb)-6]

    # First check to see if the thumbprint has the metadata we're expecting
    try:
        output = subprocess.check_output("identify -format '%c\n' "+thumb,
            shell=True)
        if MARKER in str(output):
            print("Skipping already scanned "+filename+" with "+ str(output))
            continue
    except:
        print("WARNING: failed to read existing metadata on "+thumb)

    print("Processing " + filename, flush=True)


    cap = cv2.VideoCapture(filename)

    # bestMatches contains tuples of highest score, and numberof frames above the threshold
    bestMatches = {}
    if cap.isOpened(): # try to get the first img
        rval, img = cap.read()
    else:
        rval = False

    while rval:
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
            if score > threshold:
                if label not in bestMatches.keys():
                    bestMatches[label] = (float(score), 1)
                else:
                    (bestScore, count) = bestMatches[label]
                    if bestScore < float(score):
                        bestScore = float(score)
                    count += 1
                    bestMatches[label] = (bestScore, count)

        # get next img
        rval, img = cap.read()

        # Filter out any objects we want to ignore
        for ignore in ObjectsToIgnore:
            if ignore in bestMatches:
                print("ignoring "+ignore, flush=True)
                del bestMatches[ignore]

        # Short circuit if we have good matches so we don't process the entire stream
        # to speed things up
        if hasGoodObjects(bestMatches):
            break

    if hasGoodObjects(bestMatches):
        print(bestMatches)
        if dryRun:
            continue
        output = subprocess.check_output(
            "convert -comment '"+MARKER+":"+str(bestMatches).replace("'",'\"')+"' "+thumb+" "+thumb,
            shell=True)
        print("Updated "+thumb+ " " + str(output), flush=True)
    else:
        if dryRun:
            print("Would be removing " + filename + " with no objects detected")
            continue
        print("Removing " + filename + " with no objects detected", flush=True)
        os.remove(filename)
        os.remove(thumb)

    cap.release()
    end = time.time()
    print("Running Average time per frame: "+ str((end - start)/frameCount), flush=True)

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
#sys.exit(exitCode)
