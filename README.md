##Instructions to set up:
* Install python 2.7 and python-pip.
* `cd` into the project directory and run `pip install -r requirements.txt`
* Install and start redis. Follow [this](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis)
* Run the following command to start the server: `python run.py`

##Overview
* When the server starts it will show the address on the terminal. Eg: `Running on http://172.16.201.104:5000/`
* Go to the given address in the browser. Filename and password will be asked.
* Enter any filename and password. File will be created if it doesn't exist otherwise it'll verify the name and password.
* Once the above step is completed you will be redirected to the page where you can edit the document.

##NOTE:
* The changes are being sent to the server character by character. Hence copy/paste/bulk delete is not supported.
* Only alphanumeric characters are supported (no new line).
* The changed effect is not shown instantly (not perfect).
* To see changes log in from different ip(computers).