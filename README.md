# MyFolio Server

This respository contains the python code for running the server, importing data, etc.

## Requirements

1. Apache2
2. PostgreSQL

## Installation

* Clone repository and enter directory:
    * `cd /var/www`
    * `git clone git@bitbucket.org:myfolio830/myfolio.git`
    * `cd myfolio`
* Create and activate virtual environment:
    * `virtualenv --python=/usr/bin/python3.5 server_env`
    * `source server_env/bin/activate`
* Install required Python modules:
    * `pip install -r requirements.txt`
	
## Configuration

Create a file `config.py` containing the template below with your local configuration:

---
```python
PATH = '/var/www/myfolio'                                       # Application path
VPATH = PATH + '/server_env/bin/activate_this.py'               # Virtual environment python activation path
DBURI = 'postgresql://username:password@localhost:5432/myfolio' # Database URI
```
---

## Apache Configuration

* Add the line `127.0.1.1 myfolio.local` to the file `/etc/hosts`
* Create a file `myfolio.local.conf` in the directory `/etc/apache2/sites-available` using the following template but with *yourusername*:
---
```apache
LoadModule wsgi_module "/var/www/myfolio/server_env/lib/python3.5/site-packages/mod_wsgi/server/mod_wsgi-py35.cpython-35m-x86_64-linux-gnu.so"
WSGIPythonHome "/var/www/myfolio/server_env"
WSGIPythonPath "/var/www/myfolio/server_env/lib/python3.5"

<VirtualHost *:80>
	ServerName myfolio.local

	WSGIDaemonProcess myfolio user=yourusername group=yourusername threads=5 python-path=/var/www:/var/www/myfolio:/var/www/myfolio/server_env/lib/python3.5
	WSGIProcessGroup myfolio
	WSGIScriptAlias / /var/www/myfolio/myfolio.wsgi

	<Directory /var/www/myfolio>
		WSGIProcessGroup myfolio
		WSGIApplicationGroup %{GLOBAL}
		Order deny,allow
		Allow from all
	</Directory>
</VirtualHost>
```
---
* Enable your local site: `sudo a2ensite myfolio.local.conf`
* Restart Apache: `sudo service apache2 restart`
* Check your setup by loading [myfolio.local/](http://myfolio.local/) in your browser