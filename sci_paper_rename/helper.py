import logging
import sys


def set_helper_logger(log_level):
    # logger config
    logging.basicConfig(format='[%(asctime)s] - [%(levelname)s]- %(message)s' , level=log_level)
    global logger
    logger = logging.getLogger() 
    #print(logger)
    
def print_usage():
    if logger is not None:
        logger.info('*' * 80)  # print 80 times '*'
        logger.info('   Usage:  python3 rename_sci_paper.py <TARGET_DIRECTORY>')
        logger.info('           python3 rename_sci_paper.py <PDF_FILENAME>')
        logger.info('*' * 80)
    else:
        print('ERROR: Logger was not defined. Please check if logger was set from the main file before using it')
        sys.exit(0)

def print_header():
    logger.info('*' * 80) 
    logger.info('**                         RENAME PAPERS SCIENTIFIC                           **')
    logger.info('*' * 80) 
