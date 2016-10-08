# statsenforcer
Enforcing the fancystats.



## Installation
1. This site was built using Vagrant and the "ubuntu/trusy64" VM Box
2. Once the vagrant box is up and running, install:
  * python-dev
  * postgresql 9.6
  * libpq-dev
  * python-pip
  * python-virtualenv (if using virtualenv)
3. If using virtualenv, enable first, and the install the requirements.txt file using pip
4. Obtain or create a cred.py file and including in the fls folder along with settings.py. This file should look something like:
  * DB_NAME = "db_name"
  * USER = "username"
  * PASSWORD = "password"
  * HOST = "host"
  * PORT = "portnumber"
  * SECRET_KEY = "supersecretsecretkey"
5. Enjoy!
