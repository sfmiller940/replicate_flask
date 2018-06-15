# MyFolio Server

This respository contains the python code for running the server, importing data, etc.

## Installation

Clone repository and enter directory.

* git clone git@bitbucket.org:myfolio830/myfolio.git
* cd myfolio

Create and activate virtual environment. Implementation may vary. The default name server_env is included in .gitignore.

* virtualenv --python=/usr/bin/python3.5 server_env
* source server_env/bin/activate

Install required Python modules.

* pip install -r requirements.txt

Finally edit the file config.sys so it contains the URL for your database.