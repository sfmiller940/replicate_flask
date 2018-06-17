import config

activate_this = config.PATH + '/server_env/bin/activate_this.py'
with open(activate_this) as file_:
  exec(file_.read(), dict(__file__=activate_this))

import sys
sys.path.append(config.PATH)

from run import api as application