import os


# Constaint
VERBOSE = os.environ.get("VERBOSE", "true") == "true"
DEBUG = os.environ.get("DEBUG", "false") == "true"
SCREENSHOT_IMAGES = os.environ.get("SCREENSHOT_IMAGES", "/tmp/screen.png")
TOTAL_DIVIDE = int(os.environ.get("TOTAL_DIVIDE", "3"))
RELOAD_INTERVAL = int(os.environ.get("RELOAD_INTERVAL", "3"))
