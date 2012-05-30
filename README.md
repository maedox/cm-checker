cm-checker
==========

This is a Python script for checking for new releases on the CyanogenMod downloads site (get.cm).
There are a bunch of different configuration options for email notifications, logging and so on.

There is no installation in the traditional sense as this is just a Python script. However, the
first time you run the script – by executing «python cm_checker.py» – you will be asked a few 
simple questions to populate the configuration file and then shown a usage message.

If you have a Samsung Galaxy S II like me, and would like to check if there is a new release, the
command you would want to run is «python cm_checker.py -d galaxys2». Configure you favorite task
scheduler to run that command and you will get an email when there is a new release. Of course
you need to configure the script correctly for it to send the email, but that should be easy.

Create an issue if you find anything that doesn't work or to request features.
This project is just for fun and gets updated whenever I feel like learning a new part of Python,
but all suggestions are welcome.


Disclaimer: 
This software is provided as is. It should be safe, but don't blame me if your computer blows up.
It is made for GNU/Linux based OS's, but should work on Windows with Python 2.7+, maybe 2.6+.