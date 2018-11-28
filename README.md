# replicate_flask v0.0.4

## Requirements

1. Apache2
2. PostgreSQL

## Installation

* Clone repository and enter directory:
    * `cd /var/www`
    * `git clone git@github.com:sfmiller940/replicate_flask.git`
    * `cd replicate_flask`
* Create and activate virtual environment:
    * `virtualenv --python=/usr/bin/python3.5 server_env`
    * `source server_env/bin/activate`
* Install required Python modules:
    * `pip install -r requirements.txt`
	
## Configuration

Create a file `config.py` containing the template below with your local configuration:

```python
PATH = '/var/www/replicate_flask'                                       # Application path
VPATH = PATH + '/server_env/bin/activate_this.py'               # Virtual environment python activation path
DBURI = 'postgresql://username:password@localhost:5432/replicate' # Database URI
```

## Apache Configuration

* Add the line `127.0.1.1 replicate.local` to the file `/etc/hosts`
* Create a file `replicate.local.conf` in the directory `/etc/apache2/sites-available` using the following template but with *yourusername*:
```apache
LoadModule wsgi_module "/var/www/replicate_flask/server_env/lib/python3.5/site-packages/mod_wsgi/server/mod_wsgi-py35.cpython-35m-x86_64-linux-gnu.so"
WSGIPythonHome "/var/www/replicate_flask/server_env"
WSGIPythonPath "/var/www/replicate_flask/server_env/lib/python3.5"

<VirtualHost *:80>
	ServerName replicate.local

	WSGIDaemonProcess replicate user=yourusername group=yourusername threads=5 python-path=/var/www:/var/www/replicate_flask:/var/www/replicate_flask/server_env/lib/python3.5
	WSGIProcessGroup replicate
	WSGIScriptAlias / /var/www/replicate_flask/apache.wsgi

	<Directory /var/www/replicate_flask>
		WSGIProcessGroup replicate
		WSGIApplicationGroup %{GLOBAL}
		Order deny,allow
		Allow from all
	</Directory>
</VirtualHost>
```
* Enable your local site: `sudo a2ensite replicate_flask.local.conf`
* Restart Apache: `sudo service apache2 restart`
* Check your setup by loading [replicate_flask.local/](http://replicate_flask.local/) in your browser

## Frontend App

Copy the latest stocktailor build into `/var/www/replicate_flask/app/static`