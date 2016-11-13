# statsenforcer
Enforcing the fancystats.



## Installation
1. This site was built using Vagrant and the "ubuntu/trusy64" VM Box
2. Once the vagrant box is up and running, install:
  * python-dev
  * libmysqlclient-dev
  * python-pip
  * python-virtualenv (if using virtualenv)
  * libjpeg-dev
3. If using virtualenv, enable first, and the install the requirements.txt file using pip
4. Obtain or create a cred.py file and including in the fls folder along with settings.py. This file should look something like:
  * DB_NAME = "db_name"
  * USER = "username"
  * PASSWORD = "password"
  * HOST = "host"
  * PORT = "portnumber"
  * SECRET_KEY = "supersecretsecretkey"
  * AWS_ACCESS_KEY_ID = "Your Amazon Web Services access key, as a string."
  * AWS_SECRET_ACCESS_KEY = "Your Amazon Web Services secret access key, as a string."
  * AWS_STORAGE_BUCKET_NAME = "Your Amazon Web Services storage bucket name, as a string."
5. Enjoy!
