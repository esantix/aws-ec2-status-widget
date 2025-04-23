from Foundation import NSBundle
import objc

info = NSBundle.mainBundle().infoDictionary()
info["LSBackgroundOnly"] = "1"

import pyperclip
import rumps
import json
import os
import boto3

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

    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            status = instance["State"]["Name"]
            instance_type = instance["InstanceType"]

            instances.append((instance_id, status, instance_type))

    return instances


def stop_callback(instance):
    def stop_instance(_):
        session = boto3.Session(
            profile_name=aws_config["aws_profile"],
            region_name=aws_config["region"],
        )
        ec2 = session.client("ec2")
        ec2.stop_instances(InstanceIds=[instance])
        return

    return stop_instance


def start_callback(instance):
    def start_instace(_):
        print("Starting...")
        session = boto3.Session(
            profile_name=aws_config["aws_profile"],
            region_name=aws_config["region"],
        )
        ec2 = session.client("ec2")
        ec2.start_instances(InstanceIds=[instance])
        return

    return start_instace


STATE_ICON = {"stopped": "🔴", "running": "🟢", "pending": "🔺", "stopping": "🔻"}
APP_STATE_ICON = {"on": "img/green.png", "off": "img/gray.png", }
START = "✓  Start"
STOP = "⊖  Stop"
REFRESH = "↺  Refresh"


def copy_text_to_clipboard(_):
    pyperclip.copy(aws_config["instance_id"])


class AWSStatus(rumps.App):
    def __init__(self):
        super(AWSStatus, self).__init__("EC2", icon=None)
        self.status = {"running_instances": 0, "app_status": "off"}
        self.just_ui = False
        self.icon = APP_STATE_ICON[self.status["app_status"]]

        self.timer = rumps.Timer(self.refresh, config["refresh_rate_s"])
        self.timer.start()

        self.check_timer = rumps.Timer(
            self.run_checks, config["checks"]["check_rate_m"] * 60
        )
        self.check_timer.start()

        self.refresh(None)

    def run_checks(self, _):
        """Runs notifications alerts check based on current data (refreshed on refresh_rate_s)"""

        if (
            self.status["running_instances"]
            > config["checks"]["alert_running_instances_number"]
        ):
            rumps.notification(
                "EC2 Status alert!",
                f"{self.status['on_instances']} Instances running",
                "",
            )

    def refresh(self, _):
        """Fetches EC2s data and refreshes menu"""

        for key in self.menu.keys():
            del self.menu[key]

        instances = get_all_ec2_instances_status()

        self.status["running_instances"] = 0
        for instance in instances:

            instance_id = instance[0]
            status = instance[1]
            in_type = instance[2]

            if status == "running":
                self.status["running_instances"] += 1

            instance_menu = rumps.MenuItem(
                f"{STATE_ICON[status]}  {instance_id} ({in_type})",
                callback=copy_text_to_clipboard,
            )
            instance_menu.add(rumps.separator)
            instance_menu.add(rumps.MenuItem(START, callback=None))
            instance_menu.add(rumps.MenuItem(STOP, callback=None))
            instance_menu.add(rumps.separator)

            self.update_submenu(instance_menu, instance_id, status)

            self.menu.add(instance_menu)

        if self.status["running_instances"] > 0:
            self.status["app_status"] = "on"
        else:
            self.status["app_status"] = "off"

        self.icon = APP_STATE_ICON[self.status["app_status"]]
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem(REFRESH, callback=self.refresh))

    def update_submenu(self, menu, instance_id, status):
        if status == "running":
            menu[START].set_callback(None)
            menu[START].enabled = False
            menu[STOP].set_callback(stop_callback(instance_id))
            menu[STOP].enabled = True

        elif status == "stopped":
            menu[START].set_callback(start_callback(instance_id))
            menu[STOP].set_callback(None)
            menu[START].enabled = True
            menu[STOP].enabled = False
        else:
            # Disable both if in any other state
            menu[START].set_callback(None)
            menu[STOP].set_callback(None)
            menu[START].enabled = False
            menu[STOP].enabled = False


AWSStatus().run()
