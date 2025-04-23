import json
import pyperclip
import rumps
from aws_helper import (
    get_ec2_instances_status,
    stop_instance,
    start_instace,
    instance_link,
)
from functools import partial
from constants import (
    SETTINGS_BUTTON,
    OPEN_CONSOLE,
    STATE_ICON,
    APP_STATE_ICON,
    START,
    STOP,
    REFRESH,
)
import webbrowser
from configuration import get_config
import subprocess
import logging

logging.basicConfig(level=logging.INFO)


def promt_notify(msg):
    rumps.notification("EC2 Status app", "", msg)


def empty_callback(_):
    return


def clipboard_callback(text, notify=False):
    def copy_text_to_clipboard(_):
        if notify:
            promt_notify("Data copied to clipboard")
        pyperclip.copy(text)

    return copy_text_to_clipboard


def go_to_instance_callback(instance_id, region):
    def go_to_instance(_):
        url = instance_link(instance_id, region)
        webbrowser.open(url)

    return go_to_instance


class EC2App(rumps.App):
    def __init__(self):
        super(EC2App, self).__init__("Loading...", icon=None)

        self.load_config()

        self.status = {"running_instances": 0, "app_status": "off"}
        self.just_ui = False
        self.icon = APP_STATE_ICON[self.status["app_status"]]

        self.timer = rumps.Timer(self.refresh, self.config["refresh_rate_s"])
        self.timer.start()

        self.check_timer = rumps.Timer(
            self.run_checks, self.config["checks"]["check_rate_m"] * 60
        )
        self.check_timer.start()

        self.refresh(None)

    def run_checks(self, _):
        """Runs notifications alerts check based on current data (refreshed on refresh_rate_s)"""

        if (
            self.status["running_instances"]
            > self.config["checks"]["alert_running_instances_number"]
        ):
            rumps.notification(
                "EC2 Status alert!",
                f"{self.status['on_instances']} Instances running",
                "",
            )

    def load_config(self):
        self.config = get_config()
        logging.info(self.config)
        self.aws_config = self.config["server"]["aws"]

    def open_settings_callback(self, _):
        subprocess.run(["open", self.config["default_config_path"]])
        return

    def refresh(self, _):
        """Fetches EC2s data and refreshes menu"""
        self.load_config()
        for key in self.menu.keys():
            del self.menu[key]

        try:
            instances_data = get_ec2_instances_status(self.aws_config)
        except Exception:
            notify("Unable to fetch EC2 data")
            instances_data = []
            self.menu.add(rumps.MenuItem("No data to display", callback=None))

        self.status["running_instances"] = 0
        for instance_data in instances_data:

            instance_id = instance_data["InstanceId"]

            clipboard_msg = json.dumps(instance_data, indent=2, default=str)

            display_data = {
                "Type": instance_data["InstanceType"],
                "Region": instance_data["Region"],
                "Private IP": instance_data["PrivateIpAddress"],
            }

            if instance_data["State"] == "running":
                self.status["running_instances"] += 1

            # Menu
            instance_menu = rumps.MenuItem(
                f'{STATE_ICON[instance_data["State"]]}  {instance_data["InstanceId"]}',
                callback=empty_callback,
            )

            # Sub-menus
            instance_menu.add(rumps.MenuItem(START, callback=None))
            instance_menu.add(rumps.MenuItem(STOP, callback=None))

            instance_menu.add(rumps.separator)
            for k, v in display_data.items():
                instance_menu.add(
                    rumps.MenuItem(f"{k}: {v}", callback=clipboard_callback(v))
                )

            instance_menu.add(rumps.separator)
            instance_menu.add(
                rumps.MenuItem(
                    "View on console",
                    callback=go_to_instance_callback(instance_id, instance_data["Region"]),
                )
            )
            instance_menu.add(rumps.separator)
            instance_menu.add(
                rumps.MenuItem(
                    "Copy all data", callback=clipboard_callback(clipboard_msg, True)
                )
            )

            self.update_submenu(instance_menu, instance_data)
            self.menu.add(instance_menu)

        # Main level color notification
        if self.status["running_instances"] > 0:
            self.status["app_status"] = "on"
        else:
            self.status["app_status"] = "off"

        self.icon = APP_STATE_ICON[self.status["app_status"]]
        self.menu.add(rumps.separator)
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem(REFRESH, callback=self.refresh))
        self.menu.add(
            rumps.MenuItem(OPEN_CONSOLE, callback=self.go_to_console_callback)
        )
        self.menu.add(
            rumps.MenuItem(SETTINGS_BUTTON, callback=self.open_settings_callback)
        )

    def update_submenu(self, menu, instance_data):
        if instance_data["State"] == "running":
            menu[START].set_callback(None)
            menu[START].enabled = False
            menu[STOP].set_callback(self.stop_callback(instance_data))
            menu[STOP].enabled = True

        elif instance_data["State"] == "stopped":
            menu[START].set_callback(self.start_callback(instance_data))
            menu[STOP].set_callback(None)
            menu[START].enabled = True
            menu[STOP].enabled = False
        else:
            # Disable both if in any other state
            menu[START].set_callback(None)
            menu[STOP].set_callback(None)
            menu[START].enabled = False
            menu[STOP].enabled = False

    def start_callback(self, instance_data):
        return partial(
            start_instace,
            config=self.aws_config,
            instance_id=instance_data["InstanceId"],
            region=instance_data["Region"],
        )

    def stop_callback(self, instance_data):
        return partial(
            stop_instance,
            config=self.aws_config,
            instance_id=instance_data["InstanceId"],
            region=instance_data["Region"]
        )

    def go_to_console_callback(self, _):
        url = self.aws_config["console_link"]
        webbrowser.open(url)
        return


EC2App().run()
