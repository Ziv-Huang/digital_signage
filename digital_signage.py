import os
import time
import traceback
import setproctitle
import version
from multiprocessing import Process
from src import logger
from loguru import logger as log
from src import function_registration

def launch():
    try:
        logger.LogInitialization("DEBUG" if os.path.isfile("DEBUG") else "INFO")
        log.info("Advertising Player System: {}".format(version.__version__))
        while True:
            log.info("Start process")
            p = Process(target=eventHandler, args=())
            p.start()
            p.join()
    except Exception as e:
        log.error("Main launch error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
        return False

def eventHandler():
    try:
        # Initialize loguru again because tclient multiprocessing.set_start_method would clear loguru's setting
        logger.LogInitialization("DEBUG" if os.path.isfile("DEBUG") else "INFO")
        log.info("Handle event")
        setproctitle.setproctitle("digital_signage")
        instance = function_registration.FunctionRegistration()
        instance.launch()
        log.warning("delete instance")
        del instance
        time.sleep(1)
        os.kill(os.getpid(), 9)
    except Exception as e:
        log.error("eventHandler error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
        return False

def main():
    launch()

if __name__ == "__main__":
    launch()
    