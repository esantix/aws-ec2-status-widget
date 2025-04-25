import json
import rumps
import webbrowser
import subprocess
import logging
import pyperclip

from aws_helper import *
from constants import *
from configuration import get_config

logging.basicConfig(level=logging.INFO)

def make_cb(funtion, **kwargs):
    """ Transform funtion to callback function
    """
    def callback(_):
        funtion(**kwargs)
        return
    return callback

def open_url(url):
    """ Open browser at URL
    """
    webbrowser.open(url)

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
        """Runs notifications alerts check based on current data (refreshed on refresh_rate_s)
        """
        
        # Too many instances check
        threshold = self.config["checks"]["alert_running_instances_number"]
        if (self.app_state["running_instances"] > threshold ):
            self.promt_notify(f"More than {threshold} instances running")
    
    def load_config(self):
        """ Loads configuration to class
        """
        logging.info("Refreshing configuration")
        self.config = get_config()
        self.aws_config = self.config["server"]["aws"]

        logging.debug(self.config)

    def open_settings_cb(self, _):
        """ Open configuration file
        """
        subprocess.run(["open", self.config["default_config_path"]])
        return

    def refresh(self, _):
        """Fetches EC2s data and refreshes menu
        """
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
            self.menu.add(rumps.MenuItem(NO_DATA_TEXT))

        self.app_state["running_instances"] = 0
        self.app_state["terminated_instances"] = 0

        for instance_data in instances_data:

            instance_state = instance_data["State"]
            instance_id = instance_data["InstanceId"]

            if instance_state == "terminated" and not self.config["show_terminated"]:
                self.app_state["terminated_instances"] += 1
                logging.info(f"Not showing terminated instance {instance_id}")
            
            else:
                # Menu
                instance_menu = rumps.MenuItem(f'{INSTANCE_STATE_EMOJI[instance_state]}  {instance_id}')


                display_data = {
                    "Type": instance_data.get("InstanceType", None),
                    "Region": instance_data.get("Region", None),
                    "Private IP": instance_data.get("PrivateIpAddress", None),
                }

                # Update state count
                if instance_state == "running":
                    self.app_state["running_instances"] += 1
                    
                # Sub-menus: actionable
                instance_menu.add(rumps.MenuItem(START_BUTTON_TEXT))
                instance_menu.add(rumps.MenuItem(STOP_BUTTON_TEXT))

                if instance_state == "running":
                    instance_menu[STOP_BUTTON_TEXT].set_callback(make_cb(stop_instance, config=self.aws_config, instance_id=instance_data["InstanceId"], region=instance_data["Region"]))
                elif instance_state == "stopped":
                    instance_menu[START_BUTTON_TEXT].set_callback(make_cb(start_instace, config=self.aws_config, instance_id=instance_data["InstanceId"], region=instance_data["Region"]))
 
                # Sub-menus: data
                instance_menu.add(rumps.separator)
                for k, v in display_data.items():
                    if v:
                        instance_menu.add(rumps.MenuItem(f"{k}: {v}", callback=make_cb(pyperclip.copy, text=v)))

                # Sub-menus: options buttons
                instance_menu.add(rumps.separator)
                clipboard_msg = json.dumps(instance_data, indent=2, default=str)
                instance_menu.add(rumps.MenuItem(COPY_INSTANCE_DATA_BUTTON_TEXT, callback=make_cb(pyperclip.copy, text=clipboard_msg)))
                instance_menu.add(rumps.separator)
                instance_menu.add(rumps.MenuItem(VIEW_ON_CONSOLE_BUTTON_TEXT, callback=make_cb(open_url, url=instance_url(instance_id, instance_data["Region"]))))

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
        self.menu.add(rumps.MenuItem(OPEN_CONSOLE_BUTTON_TEXT, callback=make_cb(open_url, url=self.aws_config["console_link"])))
        self.menu.add(rumps.MenuItem(SETTINGS_BUTTON_TEXT, callback=self.open_settings_cb))
    
    def promt_notify(self, msg):
        rumps.notification(NOTIFICATION_TITLE, "", msg)
        
if __name__ == "__main__":
    app = EC2Status()
    app.run()
