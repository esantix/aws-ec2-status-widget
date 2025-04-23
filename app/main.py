import json
import pyperclip
import rumps
from aws_helper import get_ec2_instances_status, stop_instance, start_instace
from functools import partial
from constants import STATE_ICON, APP_STATE_ICON, START, STOP, REFRESH

from configuration import config, aws_config


def start_callback(instance):
    return partial(
        start_instace, config=aws_config, instance=instance[0], region=instance[1]
    )


def stop_callback(instance):
    return partial(
        stop_instance, config=aws_config, instance=instance[0], region=instance[1]
    )


def empty_callback(_):
    return


def clipboard_callback(text, notify=False):
    def copy_text_to_clipboard(_):
        if notify:
            rumps.notification("EC2 Status app", "Data copied to clipboard", "", icon=f"{script_dir}/img/icon.png")
        pyperclip.copy(text)

    return copy_text_to_clipboard


class EC2App(rumps.App):
    def __init__(self):
        super(EC2App, self).__init__("Loading...", icon=None)
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

        instances = get_ec2_instances_status(aws_config)

        self.status["running_instances"] = 0
        for instance in instances:

            instance_id = instance[0]
            status = instance[1]
            in_type = instance[2]
            region = instance[3]
            data = instance[4]
            clipboard_msg = json.dumps(data, indent=2, default=str)

            display_data = {
                "Type": in_type,
                "Region": region,
                "Private IP": data["PrivateIpAddress"],
            }

            if status == "running":
                self.status["running_instances"] += 1

            # Menu
            instance_menu = rumps.MenuItem(
                f"{STATE_ICON[status]}  {instance_id}",
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
                    "Copy all data", callback=clipboard_callback(clipboard_msg, True)
                )
            )

            self.update_submenu(instance_menu, (instance_id, region), status)
            self.menu.add(instance_menu)

        # Main level color notification
        if self.status["running_instances"] > 0:
            self.status["app_status"] = "on"
        else:
            self.status["app_status"] = "off"

        self.icon = APP_STATE_ICON[self.status["app_status"]]
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem(REFRESH, callback=self.refresh))

    def update_submenu(self, menu, instance, status):
        if status == "running":
            menu[START].set_callback(None)
            menu[START].enabled = False
            menu[STOP].set_callback(stop_callback(instance))
            menu[STOP].enabled = True

        elif status == "stopped":
            menu[START].set_callback(start_callback(instance))
            menu[STOP].set_callback(None)
            menu[START].enabled = True
            menu[STOP].enabled = False
        else:
            # Disable both if in any other state
            menu[START].set_callback(None)
            menu[STOP].set_callback(None)
            menu[START].enabled = False
            menu[STOP].enabled = False


EC2App().run()
