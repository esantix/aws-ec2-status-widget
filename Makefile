
load:
	@ launchctl load com.app.ec2status.plist

unload:
	@ launchctl unload com.app.ec2status.plist

reload:
	@ launchctl unload com.app.ec2status.plist
	@ launchctl load com.app.ec2status.plist