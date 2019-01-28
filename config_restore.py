"""
config_restore.py saves a backup of your config to an attached USB drive
It saves .bins to /var/media/config_backups/
How it works: Every 20 seconds, it checks to see if a config change was made.  If a change was made, it saves a backup
of your old config.  Tada!  The magic happens in checkChange()

Important! An admin user of user: admin, pass: 123$Abcd is created on every bin file saved by this!

Known issues: reloading configurations doesn't play super nice with NetCloud Manager.  You may need to clear the config
in NCM for the uploaded config not to get overridden.  This is an issue with NetCloud as far as I am concerned.
A potential workaround could be to set "ecm": { "config_version": config_version+1}.  I haven't test that though, and
this version of the program doesn't have that feature.
"""

# A try/except is wrapped around the imports to catch an
# attempt to import a file or library that does not exist
# in NCOS. Very useful during app development if one is
# adding python libraries.
try:
    import cs
    import sys
    import traceback
    import argparse
    import os
    import time
    import json
    import zlib

    from app_logging import AppLogger

except Exception as ex:
    # Output DEBUG logs indicating what import failed. Use the logging in the
    # CSClient since app_logging may not be loaded.
    cs.CSClient().log('app_template.py', 'Import failure: {}'.format(ex))
    cs.CSClient().log('app_template.py', 'Traceback: {}'.format(traceback.format_exc()))
    sys.exit(-1)


# Create an AppLogger for logging to syslog in NCOS.
log = AppLogger()


# Add functionality to execute when the app is started
def start_app():
    try:
        log.debug('Started config_restore.py')
        log.debug('Starting checkChange()')
        # dir = '/var/media/config_backups/'
        # n = len(os.listdir(dir))
        # log.debug('there are {} files in {}'.format(n, dir))
        # Try and launch our checkChange() function to see if a config change is made
        # for f in os.listdir(dir):
        #     log.debug('file in {}: {}'.format(dir,f))
        try:
            checkChange()
        except Exception as e:
            log.error('Exception during checkChange()! exception: {}'.format(e))
            raise

    except Exception as e:
        log.error('Exception during start_app()! exception: {}'.format(e))
        raise


# Add functionality to execute when the app is stopped
def stop_app():
    try:
        log.debug('stop_app()')

    except Exception as e:
        log.error('Exception during stop_app()! exception: {}'.format(e))
        raise


# This function will take action based on the command parameter.
def action(command):
    try:
        # Log the action for the app.
        log.debug('action({})'.format(command))

        if command == 'start':
            # Call the start function when the app is started.
            start_app()

        elif command == 'stop':
            # Call the stop function when the app is stopped.
            stop_app()

    except Exception as e:
        log.error('Exception during {}! exception: {}'.format(command, e))
        raise


def checkChange():
    while True:
        config_1 = cs.CSClient().get('/config/')
        log.debug('Saving current config for comparison, check diff in 20 seconds')
        time.sleep(20)
        config_2 = cs.CSClient().get('/config/')
        # Check the configs, if there's a difference save the old config to backup.json
        if config_1 != config_2:
            log.debug('Difference detected, saving backup of old config to /var/media/config_backups/')
            # Try and create folder in /var/media/ for configs if it doesnt exist.
            try:
                if not os.path.exists('/var/media/config_backups/'):
                    try:
                        os.makedirs('/var/media/config_backups/')
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            raise
            except Exception as e:
                log.error('Exception creating /var/media/config_backups!'
                          'Is a usb stick attached? exception: {}'.format(e))
            # save backup
            try:
                # dump our config to a json file
                json_file = json.dumps(config_1)
                # convert it to a python dictionary
                py_dict = json.loads(json_file)
                # grab just the data tree from it
                data = py_dict["data"]
                # create our config file. its a nested list/dict right now
                config_file = [{
                        "fw_info": {
                            "major_version": 6,
                            "minor_version": 6,
                            "patch_version": 4,
                            "build_version": 0
                        },
                        "config": {

                            }
                        },
                        []
                        ]

                # create a default user to override the hashed password
                default_user = [{'group': 'admin', 'username': 'admin', 'password': '123$Abcd'}]

                # set the config tree in it to equal our data tree
                config_file[0]["config"] = data
                # add the default user
                config_file[0]["config"]["system"]["users"] = default_user

                # check how many files we have in our folder
                n = len(os.listdir('/var/media/config_backups/'))
                os.chdir('/var/media/config_backups/')

                # dump to json, uncomment this if you want a .json instead of a .bin
                # with open('backup{}.json'.format(n), 'w') as f:
                #     json.dump(config_file, f)
                
                # dump to bin
                with open('backup{}.bin'.format(n), 'wb') as f:
                    f.write(zlib.compress(json.dumps(config_file).encode()))
            except Exception as e:
                log.error('Exception during save! exception: {}'.format(e))
                raise

        else:
            log.debug('No difference detected in configuration')


# The main entry point for app_template.py This will be executed when the
# application is started or stopped as defined in the start.sh and stop.sh
# scripts. It expects either a 'start' or 'stop' argument.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('opt')
    args = parser.parse_args()

    opt = args.opt.strip()
    if opt not in ['start', 'stop']:
        log.debug('Failed to run command: {}'.format(opt))
        exit()

    action(opt)

    log.debug('App is exiting')
