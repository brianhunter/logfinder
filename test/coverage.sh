#../bi../bash

sudo apt-get install python-pip -y && sudo pip install coverage

coverage erase && coverage run ../logfinder.py && coverage run -a ../logfinder.py syslog syslog.old | wc -l && coverage run -a ../logfinder.py foo9 bar8 ; coverage report -m && coverage html

