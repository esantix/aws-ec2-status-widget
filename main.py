from Foundation import NSBundle
import objc

info = NSBundle.mainBundle().infoDictionary()
info["LSBackgroundOnly"] = "1"
import pyperclip


import rumps
import json
import os
import logging as lg
import boto3
import time

script_dir = os.path.dirname(os.path.abspath(__file__))

with open(f"{script_dir}/config.json", "r") as f:
    config = json.load(f)

aws_config = config["cloud_config"]






def get_all_ec2_instances_status():
    session = boto3.Session(
        profile_name=aws_config["aws_profile"],
        region_name=aws_config["region"],
    )
    ec2 = session.client("ec2")
    response = ec2.describe_instances()

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            if instance_id == aws_config["instance_id"]:
                return instance["State"]["Name"]

    return "not found"


def stop_instance():
    session = boto3.Session(
        profile_name=aws_config["aws_profile"],
        region_name=aws_config["region"],
    )
    ec2 = session.client("ec2")
    ec2.stop_instances(InstanceIds=[aws_config["instance_id"]])
    return


def start_instace():
    print("Starting...")
    session = boto3.Session(
        profile_name=aws_config["aws_profile"],
        region_name=aws_config["region"],
    )
    ec2 = session.client("ec2")
    ec2.start_instances(InstanceIds=[aws_config["instance_id"]])
    return


STATE_ICON = {"stopped": "⊖", "running": "✓", "pending": "↑", "stopping": "↓"}


START = "✓  Start"
STOP = "⊖  Stop"
REFRESH = "↺  Refresh"


def copy_text_to_clipboard(_):
    pyperclip.copy(aws_config['instance_id'])


class AWSStatus(rumps.App):
    def __init__(self):
        super(AWSStatus, self).__init__("Loading..", icon=None)
        self.status = ""

        self.timer = rumps.Timer(self.refresh, 10.0)
        self.timer.start()

        self.info_item = rumps.MenuItem(f"Instance ID: {aws_config['instance_id']}", callback=copy_text_to_clipboard)
        self.menu.add(self.info_item)
        self.status_item = rumps.MenuItem(f"Status: {self.status} ", callback=self.do_nothing)
        self.menu.add(self.status_item)
        self.menu.add(rumps.separator)

        self.menu.add(rumps.MenuItem(START, callback=self.on_start))
        self.menu.add(rumps.MenuItem(STOP, callback=self.on_stop))
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem(REFRESH, callback=self.on_refresh))
        self.menu.add(rumps.separator)

        # Add non-interactive info item

    def update_status(self, new_status):

        self.title = f"VM {STATE_ICON.get(new_status, new_status)}"
        self.status = new_status
        self.status_item.title = f"Status: {self.status}"
        if self.status == "running":
            self.menu[START].set_callback(None)
            self.menu[START].enabled = False
            self.menu[STOP].set_callback(self.on_stop)
            self.menu[STOP].enabled = True

        elif self.status == "stopped":
            self.menu[START].set_callback(self.on_start)
            self.menu[STOP].set_callback(None)
            self.menu[START].enabled = True
            self.menu[STOP].enabled = False
        else:
            # Disable both if in any other state
            self.menu[START].set_callback(None)
            self.menu[STOP].set_callback(None)
            self.menu[START].enabled = False
            self.menu[STOP].enabled = False

    def refresh(self, _=None):
        self.title = "Refreshing..."
        new_status = get_all_ec2_instances_status()
        self.update_status(new_status)

    def on_refresh(self, _):
        self.refresh()

    def on_start(self, _):
        start_instace()
        self.refresh()

    def on_stop(self, _):
        stop_instance()
        self.refresh()
    
    def do_nothing(self, _):
        pass  # placeholder to keep menu item enabled



AWSStatus().run()
