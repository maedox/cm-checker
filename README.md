# cm-checker

This is a Python script for checking for new releases on the CyanogenMod downloads site (get.cm).
There are a bunch of different configuration options for email notifications, logging and so on.

There is no installation in the traditional sense as this is just a Python script. However, the
first time you run the script – by executing `python cm_checker.py` – you will be asked a few 
simple questions to populate the configuration file.

If you have a Samsung Galaxy S II like me, and would like to check if there is a new release, the
command you would want to run is `python cm_checker.py -d galaxys2`. Configure you favorite task
scheduler to run that command and you will get an email when there is a new release. Remember to
add the -n option in the scheduler to disable printing release names on screen/stdout.

Of course you need to configure the script correctly for it to send the email, but that's easy.

Create an issue if you find anything that doesn't work or to request features.
This project is just for fun and gets updated whenever I feel like learning a new part of Python,
but all suggestions are welcome. If my code sucks for whatever reason, please tell me.


## Disclaimer: 
This software is provided as is. It should be safe, but don't blame me if your computer blows up.
It is made for GNU/Linux based OS's, but should work on Windows with Python 2.7+, maybe 2.6+.


## Usage: 
```python cm_checker.py -d device-name```

Find you device name at `http://get.cm`

## Crontab example for checking every other hour:
### Open your crontab:
```$ crontab -e```
Then add: 
```00 */2 * * * ~/bin/cm_checker.py -n -d device```


## Tl;dr:
No installation needed, just run it. No guarantees what so ever. Let me know what you think.

```Twitter: https://twitter.com/#!/maedox/
Google+: https://plus.google.com/109034374937381314474/```
