import os
import logging
#######################################################
# Created by: Escualo of Stack Overflow
# Edited by: rmtheis of Stack Overflow
# Source: https://stackoverflow.com/a/9321890/4356359
#######################################################

if not os.path.exists('logs'):
    os.makedirs('logs')

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
                    datefmt='%m-%d-%y %H:%M',
                    filename='logs/history.log',
                    filemode='a')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-8s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

# Now, we can log to the root logger, or any other logger. First the root...
# logging.info('Jackdaws love my big sphinx of quartz.')

# Now, define a couple of other loggers which might represent areas in your
# application:

# logger1 = logging.getLogger('myapp.area1')
# logger2 = logging.getLogger('myapp.area2')

# logger1.debug('Quick zephyrs blow, vexing daft Jim.')
# logger1.info('How quickly daft jumping zebras vex.')
# logger2.warning('Jail zesty vixen who grabbed pay from quack.')
# logger2.error('The five boxing wizards jump quickly.')

log = logging.getLogger('pdf2csv')