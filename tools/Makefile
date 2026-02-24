DIR := ${CURDIR}
CURRENT_UID := $$(id -u)
CURRENT_GID := $$(id -g)

all: run

build:
	docker build -t icnmltools .

run: build
	docker run -it --rm -v $(DIR):/icnml --net host icnmltools python

bash: build
	docker run -it --rm -v $(DIR):/icnml --net host icnmltools bash

