

PYTHON = python3

.PHONY = build run clean full

.DEFAULT_GOAL = help


full: build run

build: 
	docker rm foo ; docker rmi ncei-weather-img; docker build -t ncei-weather-img . 
	
run:
	docker run -it -v $$PWD/data:/app/scripts/data --name="foo" ncei-weather-img /bin/bash

clean: 
	rm -rf data
	docker rm foo
	docker rmi ncei-weather-img
