.PHONY: load
load:
	@ launchctl load com.app.ec2status.plist
	
.PHONY: unload
unload:
	@ launchctl unload com.app.ec2status.plist

reload: unload load
