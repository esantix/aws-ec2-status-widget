
load:
	@ launchctl load /Users/santiagoechevarria/Library/LaunchAgents/com.santiago.ec2status.plist

unload:
	@ launchctl unload /Users/santiagoechevarria/Library/LaunchAgents/com.santiago.ec2status.plist

reload:
	@ launchctl unload /Users/santiagoechevarria/Library/LaunchAgents/com.santiago.ec2status.plist
	@ launchctl load /Users/santiagoechevarria/Library/LaunchAgents/com.santiago.ec2status.plist