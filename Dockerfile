FROM ubuntu:xenial as base
RUN apt-get update && apt-get install -y \
    wget

RUN mkdir /src /yolo
# Get the weight files (move to second stage once this is sorted out)
RUN cd /yolo && \
    wget https://pjreddie.com/media/files/yolov3-tiny.weights && \
    wget https://pjreddie.com/media/files/yolov3.weights

FROM base
RUN apt-get update && apt-get install -y \
    cmake \
    ffmpeg \
    g++ \
    gcc \
    git \
    libavcodec-dev \
    libavdevice-dev \
    libavformat-dev \
    libglib2.0 \
    libsm6 \
    libxrender1 \
    make \
    python3 \
    python3-dev \
    python3-numpy


RUN git clone https://github.com/opencv/opencv.git src/opencv
RUN mkdir src/opencv/build && cd /src/opencv/build && \
    cmake ../ && \
    make && \
    make install



RUN git clone https://github.com/pjreddie/darknet /src/darknet
WORKDIR /src/darknet
# TODO - enable opencv maybe?
RUN make

# TODO move up
#RUN pip3 install opencv-python-headless

COPY obj_detect.py /bin/obj_detect

ENTRYPOINT ["python3","/bin/obj_detect"]
