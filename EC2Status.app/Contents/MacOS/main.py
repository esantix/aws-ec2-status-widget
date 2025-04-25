import json
import rumps
from aws_helper import (
    get_ec2_instances_status,
    stop_instance,
    start_instace,
    instance_link,
)
from functools import partial
from constants import *
import webbrowser
from configuration import get_config
import subprocess
import logging
import pyperclip

logging.basicConfig(level=logging.INFO)


class EC2Status(rumps.App):
    def __init__(self):
        super(EC2Status, self).__init__("", icon=APP_STATE_ICON["off"])

        self.load_config()

        self.app_state = {
            "running_instances": 0, 
            "vm_on": False
            }

        # Refresh app data
        self.timer = rumps.Timer(self.refresh, self.config["refresh_rate_s"])
        self.timer.start()

        # Checks
        self.check_timer = rumps.Timer(
            self.run_checks, self.config["checks"]["check_rate_m"] * 60
        )
        self.check_timer.start()

        self.refresh(None)

    def run_checks(self, _):
        """Runs notifications alerts check based on current data (refreshed on refresh_rate_s)"""
        
        # Too many instances check
        threshold = self.config["checks"]["alert_running_instances_number"]
        if (self.app_state["running_instances"] > threshold ):
            self.promt_notify(f"More than {threshold} instances running")
    

    def load_config(self):
        self.config = get_config()
        logging.info("Loading new config")
        logging.debug(self.config)
        self.aws_config = self.config["server"]["aws"]

    def open_settings_cb(self, _):
        subprocess.run(["open", self.config["default_config_path"]])
        return

    def refresh(self, _):
        """Fetches EC2s data and refreshes menu"""
        self.load_config()
        for key in self.menu.keys():
            del self.menu[key]

        self.timer.interval = self.config["refresh_rate_s"]
        self.check_timer.interval = self.config["checks"]["check_rate_m"] * 60

        try:
            instances_data = get_ec2_instances_status(self.aws_config)
        except Exception:
            self.promt_notify(FETCH_ERROR_MSG)
            logging.error("Unable to fetch EC2 data")
            instances_data = []
            self.menu.add(rumps.MenuItem(NO_DATA_TEXT, callback=None))

        self.app_state["running_instances"] = 0
        self.app_state["terminated_instances"] = 0

        for instance_data in instances_data:

            if instance_data["State"] == "terminated" and  not self.config["show_terminated"]:
                self.app_state["terminated_instances"] += 1
                logging.info(f"Not showing terminated instance {instance_data['InstanceId']}")
            
            else:
                # Menu
                instance_menu = rumps.MenuItem(
                    f'{VM_STATE_ICON.get(instance_data["State"], "")}  {instance_data["InstanceId"]}',
                    callback=self.empty_cb,
                )


                display_data = {
                    "Type": instance_data.get("InstanceType", None),
                    "Region": instance_data.get("Region", None),
                    "Private IP": instance_data.get("PrivateIpAddress", None),
                }

                # Update state count
                if instance_data["State"] == "running":
                    self.app_state["running_instances"] += 1
                    
                # Sub-menus: actionable
                instance_menu.add(rumps.MenuItem(START_BUTTON_TEXT, callback=None))
                instance_menu.add(rumps.MenuItem(STOP_BUTTON_TEXT, callback=None))

                if instance_data["State"] == "running":
                    instance_menu[START_BUTTON_TEXT].set_callback(self.start_cb(instance_data))
                elif instance_data["State"] == "stopped":
                    instance_menu[STOP_BUTTON_TEXT].set_callback(self.stop_cb(instance_data))
 
                # Sub-menus: data
                instance_menu.add(rumps.separator)
                for k, v in display_data.items():
                    if v is not None:
                        instance_menu.add(
                            rumps.MenuItem(f"{k}: {v}", callback=self.clipboard_cb(v))
                        )

                # Sub-menus: options buttons
                instance_menu.add(rumps.separator)
                instance_menu.add(rumps.MenuItem(VIEW_ON_CONSOLE_BUTTON_TEXT, callback=self.go_to_instance_cb(instance_data["InstanceId"], instance_data["Region"])))
                instance_menu.add(rumps.separator)
                clipboard_msg = json.dumps(instance_data, indent=2, default=str)
                instance_menu.add(rumps.MenuItem(COPY_INSTANCE_DATA_BUTTON_TEXT, callback=self.clipboard_cb(clipboard_msg, True)))

                self.menu.add(instance_menu)

        # Main level color notification
        if self.app_state["running_instances"] > 0:
            self.app_state["vm_on"] = True
            self.icon = APP_STATE_ICON["on"]
        else:
            self.app_state["vm_on"] = False
            self.icon = APP_STATE_ICON["off"]

        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem(REFRESH_BUTTON_TEXT, callback=self.refresh))
        self.menu.add(rumps.MenuItem(OPEN_CONSOLE_BUTTON_TEXT, callback=self.go_to_console_cb))
        self.menu.add(rumps.MenuItem(SETTINGS_BUTTON_TEXT, callback=self.open_settings_cb))

    def start_cb(self, instance_data):
        return partial(
            start_instace,
            config=self.aws_config,
            instance_id=instance_data["InstanceId"],
            region=instance_data["Region"],
        )

    def stop_cb(self, instance_data):
        return partial(
            stop_instance,
            config=self.aws_config,
            instance_id=instance_data["InstanceId"],
            region=instance_data["Region"],
        )

    def go_to_console_cb(self, _):
        url = self.aws_config["console_link"]
        webbrowser.open(url)
        return

    def go_to_instance_cb(self, instance_id, region):
        def go_to_instance(_):
            url = instance_link(instance_id, region)
            webbrowser.open(url)

        return go_to_instance
    
    def promt_notify(self, msg):
        rumps.notification(NOTIFICATION_TITLE, "", msg)

    def empty_cb(self, _):
        return

    def clipboard_cb(self, text, notify=False):
        def copy_text_to_clipboard(_):
            if notify:
                self.promt_notify("Data copied to clipboard")
            pyperclip.copy(text)

        return copy_text_to_clipboard


if __name__ == "__main__":
    app = EC2Status()
    app.run()
