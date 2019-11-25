# Derived from https://github.com/madhawav/YOLO3-4-Py/blob/master/docker/Dockerfile-gpu
FROM nvidia/cuda:9.0-cudnn7-devel

## Dependency installation ##
RUN apt-get update && apt-get install -y \
	build-essential \
	cmake \
	ffmpeg \
	git \
	imagemagick \
	libavcodec-dev \
	libavformat-dev \
	libdc1394-22-dev \
	libgdal-dev \
	libjasper-dev \
	libjpeg-dev \
	libopencore-amrnb-dev \
	libopencore-amrwb-dev \
	libopenexr-dev \
	libpng-dev \
	libswscale-dev \
	libtheora-dev \
	libtiff5-dev \
	libv4l-dev \
	libvorbis-dev \
	libvtk6-dev \
	libwebp-dev \
	libx264-dev \
	libxine2-dev \
	libxvidcore-dev \
	pkg-config \
	python3.5 \
	python3-dev \
	python3-numpy \
	python3-pip \
	python3-tk \
	python-dev \
	python-numpy \
	python-tk \
	qt5-default \
	unzip \
	wget \
	yasm \
	zlib1g-dev

ARG OPENCV_VERSION=3.4.8
RUN wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip && \
	unzip ${OPENCV_VERSION}.zip && \
	rm ${OPENCV_VERSION}.zip && \
	mkdir /opencv-${OPENCV_VERSION}/build
RUN cd /opencv-${OPENCV_VERSION}/build && \
	cmake \
	-D BUILD_EXAMPLES=OFF \
	-D WITH_FFMPEG=ON  \
	.. && \
	make -j4 && \
	make install && \
	ldconfig


## Downloading and compiling darknet ##
RUN git clone https://github.com/pjreddie/darknet.git /darknet
RUN cd /darknet && \
	sed -i '/GPU=0/c\GPU=1' Makefile && \
	sed -i '/OPENCV=0/c\OPENCV=1' Makefile && \
	make
ENV DARKNET_HOME /darknet
ENV LD_LIBRARY_PATH /darknet

## Download and compile YOLO3-4-Py ##
RUN git clone https://github.com/madhawav/YOLO3-4-Py.git /YOLO3-4-Py
RUN pip3 install pkgconfig cython numpy
ENV GPU 1
ENV OPENCV 1
RUN cd /YOLO3-4-Py && \
	python3 setup.py build_ext --inplace

## Download Models ##
ADD ./download_models.sh /YOLO3-4-Py/download_models.sh
RUN cd /YOLO3-4-Py/ && sh download_models.sh

## Run test ##
ADD ./obj_detect.py /YOLO3-4-Py/
WORKDIR /YOLO3-4-Py/
ENTRYPOINT ["python3","/YOLO3-4-Py/obj_detect.py"]
