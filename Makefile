ORG=dhiltgen
IMAGE=cv
DOCKER_BUILDKIT=1
export DOCKER_BUILDKIT

# Override to append additional tag data
EXTRA_TAG=""

help:
	@echo "Either 'make cpu' or 'make gpu'"
	@echo "Either 'make push-cpu' or 'make push-gpu'"



cpu:
	docker build \
	    -t $(ORG)/$(IMAGE):cpu$(EXTRA_TAG) \
	    --build-arg BASE_IMAGE=ubuntu:18.04 \
	    --build-arg OPENCV_VERSION=3.4.8 \
	    --build-arg GPU=0 \
	    .

gpu:
	docker build \
	    -t $(ORG)/$(IMAGE):gpu$(EXTRA_TAG) \
	    --build-arg BASE_IMAGE=nvidia/cuda:10.1-cudnn7-devel \
	    --build-arg OPENCV_VERSION=3.4.8 \
	    --build-arg GPU=1 \
	    .


push-cpu:
	docker push $(ORG)/$(IMAGE):cpu$(EXTRA_TAG)

push-gpu:
	docker push $(ORG)/$(IMAGE):gpu$(EXTRA_TAG)
