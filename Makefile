.PHONY: build push test

REGISTRY ?= crafters.cr.cloud.ru
VERSION ?= latest
PLATFORMS ?= linux/amd64
PREFIX ?= dev-
IMAGE_NAME ?= $(PREFIX)mcp-object-storage

build:
	docker buildx build \
		--platform $(PLATFORMS) \
		-t $(IMAGE_NAME):$(VERSION) .
	@echo "Image $(IMAGE_NAME):$(VERSION) built successfully"

push: build
	docker tag $(IMAGE_NAME):$(VERSION) $(REGISTRY)/$(IMAGE_NAME):$(VERSION)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(VERSION)
	@echo "Image pushed to $(REGISTRY)/$(IMAGE_NAME):$(VERSION)"

test:
	uv run pytest tests/ -v

