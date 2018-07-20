import config

# Activate virtual environment
with open(config.VPATH) as file_:
  exec(file_.read(), dict(__file__=config.VPATH))

# Add app to path
import sys
sys.path.append(config.PATH)

# Run app
from runServer import app as application