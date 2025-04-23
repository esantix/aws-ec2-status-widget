.PHONY: load
load:
	open EC2Status.app

kill:
	ps aux | grep EC2Status | grep -v grep | awk '{print $2}' | xargs kill

local:
	./EC2Status.app/Contents/MacOS/EC2Status
