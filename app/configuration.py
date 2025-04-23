import json
import os
from constants import DEFAULT_CONFIG_PATH
from Foundation import NSBundle
import logging

# Set app to run on background
info = NSBundle.mainBundle().infoDictionary()
info["LSBackgroundOnly"] = "1"


def get_config():
    # Load app config
    home_dir = os.path.expanduser("~")
    default_config_path = f"{home_dir}/{DEFAULT_CONFIG_PATH}"
    script_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        with open(default_config_path, "r") as f:
            config = json.load(f)
    except Exception:
        logging.error("Unable to fetch config path. Using defaults")
        with open(f"{script_dir}/config/defaults_config.json", "r") as f:
            config = json.load(f)

    config["default_config_path"] = default_config_path
    return config