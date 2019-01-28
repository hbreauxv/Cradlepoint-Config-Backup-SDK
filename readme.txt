Application Name
================
config_backup


Application Version
===================
1.0


NCOS Devices Supported
======================
ALL


External Requirements
=====================
None


Application Purpose
===================
config_restore.py saves a backup of your config to an attached USB drive
It saves .bins to /var/media/config_backups/
How it works: Every 20 seconds, it checks to see if a config change was made.  If a change was made, it saves a backup
of your old config.  

Important! An admin user of user: admin, pass: 123$Abcd is created on every bin file saved!

Known issues: reloading configurations doesn't play super nice with NetCloud Manager.  You may need to clear the config
in NCM for the uploaded config not to get overridden.  This is an issue with NetCloud as far as I am concerned.
A potential workaround could be to set "ecm": { "config_version": config_version+1}.  I haven't test that though, and
this version of the program doesn't have that feature.


Expected Output
===============
Your USB drive should get populated with a backup[x].bin file when you change configuration settings.  

