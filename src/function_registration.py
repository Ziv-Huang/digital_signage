import traceback
import time
from loguru import logger as log
from src import player, IPC_server

class FunctionRegistration:
    def __init__(self):

        self.HEARTBEAT = None
        self.__ipc_instance = IPC_server.IPC_server()
        self.__player_instance = player.player(self.__ipc_instance)
        # self.read_configuration()

    def register_thread(self):
        try:
            log.info("Register thread")
            self.__ipc_instance.register_IPC_server_thread()
            self.__player_instance.register_player_thread()
        except Exception as e:
            log.error("registerThread error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def launch(self):
        try:
            self.register_thread()
            # event wait until need to restart system
            while True:
                log.info("digital signage: heartbeats")
                time.sleep(1800)

            log.warning("digital_signage reload system!!!")
        except Exception as e:
            log.error("launch error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False