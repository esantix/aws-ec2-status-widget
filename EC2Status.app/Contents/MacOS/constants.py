
# Icons
INSTANCE_STATE_EMOJI = {
    "pending": "🟠", 
    "running": "🟢", 
    "stopping": "⭕️", 
    "stopped": "🔴", 
    "shutting-down": "🔻",
    "terminated": "❌",
    "unknown": "❔"
    }

APP_STATE_ICON = {
    "on": "img/green.png", 
    "off": "img/gray.png" 
    }

# Menu texts
REFRESH_BUTTON_TEXT = "Refresh"
OPEN_CONSOLE_BUTTON_TEXT = "Open console"
SETTINGS_BUTTON_TEXT = "Open settings"
NO_DATA_TEXT = "No data to display"
# Sub menu texts
START_BUTTON_TEXT = "✓  Start"
STOP_BUTTON_TEXT = "⊖  Stop"
COPY_INSTANCE_DATA_BUTTON_TEXT = "Copy EC2 data"
VIEW_ON_CONSOLE_BUTTON_TEXT = "View on console"

# Notification messages
NOTIFICATION_TITLE = "EC2 Status"
FETCH_ERROR_MSG = "⚠️ Unable to fetch EC2 data"
DATA_TO_CLIPBOARD_MSG = "Data copied to clipboard"

# App values
APP_CONFIG_PATH = ".ec2app/config.json" # Relative to Home