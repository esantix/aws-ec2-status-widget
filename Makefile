.PHONY: load
load:
	@ launchctl load com.app.ec2status.plist
	
.PHONY: unload
unload:
	@ launchctl unload com.app.ec2status.plist

setconf:
	cp app/config/defaults_config.json ~/.ec2app/config.json

reload: unload load
