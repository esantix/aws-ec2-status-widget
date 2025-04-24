# AWS EC2's status widget [WIP]
An MacOS top bar widget to easily see and control your EC2 instances.


## Functionalities

- Display green icon if any EC2 is running
- Display EC2 status for every instance in specified regions
- Stop / Start instances
- Copy instance full description to clipboard


## Demo
#### Off
![image](./img/screenshots/off.png)

#### On
![image](./img/screenshots/on.png)


## Setup
The app requires an IAM user with permisions to fetch EC2 data. A recommended way to achieve this is:
- Create and IAM 
- Attach a policy equivalent to [this policy](./setup/policy.json) (RO + start/stop privileges over EC2).
- Create key pair
- Add [credentials block](./setup/credentials) to your ~/.aws/credentials file

- Copy [default_config.json](./EC2Status.app/Contents/config/defaults_config.json) to ~/.ec2app/config.json and edit _aws_profile_ field. (Config file can be accessed from app menu)


## Installation
To install app ensure your python environment satisfies [requirements.txt](./setup/requirements.txt) or create a new virtual env and reference it on [EC2Status executable path](EC2Status.app/Contents/MacOS/EC2Status)

Recomended steps:

- Make virtual environment
```sh
python3 -m venv ./EC2Status.app/Contents/MacOS/venv
source ./EC2Status.app/Contents/MacOS/venv/bin/activate
pip3 install -r setup/requirements.txt
```


- Try app on terminal
```bash
./EC2Status.app/Contents/MacOS/EC2Status
```

- Or load app
```bash
open EC2Status.app
```

