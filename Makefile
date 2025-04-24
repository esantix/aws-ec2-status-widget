.PHONY: load
load:
	open EC2Status.app

kill:
	ps aux | grep EC2Status | grep -v grep | awk '{print $2}' | xargs kill

local:
	./EC2Status.app/Contents/MacOS/EC2Status

venv:
	python3 -m venv ./EC2Status.app/Contents/MacOS/venv
	source ./EC2Status.app/Contents/MacOS/venv/bin/activate
	pip3 install -r setup/requirements.txt