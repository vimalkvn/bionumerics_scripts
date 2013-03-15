"""Using the python logging module"""
import bns
import os.path
import logging

#setup logging
LOG_FILENAME = os.path.join(bns.Database.Db.Info.Path, 'logging-example.txt')
formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s', 
							  '%Y-%m-%d %H:%M')
if os.path.exists(LOG_FILENAME):
	LOG_MODE = 'a'
else:
	LOG_MODE = 'w'

log = logging.getLogger('log')
#change this to logging.DEBUG for debugging!
log.setLevel(logging.INFO)

handler = logging.FileHandler(LOG_FILENAME, mode=LOG_MODE)
handler.setFormatter(formatter)	
log.addHandler(handler)

#Now we write some messages to log
log.info('This is an info message')
log.warn('A warning')
log.critical('An error has occured')
log.debug('This is from main')

#this is important
handler.close()
log.removeHandler(handler)

