import threading
import asyncio
from websocket_server import WebsocketServer
import time
import os
import json
import traceback
from loguru import logger as log

class IPC_server:
    def __init__(self):
        self.__users = set()
        self.__packet = None
        self.__video_end = None
        self.__lock_users = threading.Lock()
        self.__event_users = threading.Event()
        self.__lock_data = threading.Lock()
        self.__event_data = threading.Event()
        self.__lock_video_end = threading.Lock()
        self.__event_video_end = threading.Event()

    def get_users(self):
        try:
            log.debug("get users")
            self.__event_users.wait()
            self.__event_users.clear()
            with self.__lock_users:
                return self.__users
        except Exception as e:
            log.error("get users error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def set_packet(self,input):
        try:
            log.debug("set data")
            with self.__lock_data:
                self.__packet = input
            self.__event_data.set()
        except Exception as e:
            log.error("set data error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def get_packet(self):
        try:
            log.debug("get data")
            self.__event_data.wait()
            self.__event_data.clear()
            with self.__lock_data:
                return self.__packet
        except Exception as e:
            log.error("get data error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def set_video_end(self,input):
        try:
            log.debug("set video_end")
            with self.__lock_video_end:
                self.__video_end = input
            self.__event_video_end.set()
        except Exception as e:
            log.error("set video_end error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def get_video_end(self):
        try:
            log.debug("get video_end")
            self.__event_video_end.wait()
            self.__event_video_end.clear()
            with self.__lock_video_end:
                return self.__video_end
        except Exception as e:
            log.error("get video_end error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def register(self,client):
        try:
            log.debug("register users")
            with self.__lock_users:
                self.__users.add(client["handler"])
            self.__event_users.set()
            log.info("register user: {}".format(client))
        except Exception as e:
            log.error("register error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def unregister(self,client):
        try:
            log.debug("register users")
            with self.__lock_users:
                self.__users.remove(client["handler"])
            self.__event_users.set()
            log.info("unregister user: {}".format(client))
        except Exception as e:
            log.error("unregister error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def notify_users(self,server):
        try:
            while True:
                data = self.get_packet()
                message = json.dumps(data)
                server.send_message_to_all(message)

        except Exception as e:
            log.error("notify users error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def new_client(self,client, server):
        self.register(client)
        log.info("Client(%d) has joined." % client['id'])


    def client_left(self,client, server):
        self.unregister(client)
        log.info("Client(%d) disconnected" % client['id'])


    def message_back(self,client, server, message):
        log.info("Client(%d) said: %s" % (client['id'], message))
        if message == "video_end":
            self.set_video_end(True)


    def launch_server(self):
        # 新建一个WebsocketServer对象，第一个参数是端口号，第二个参数是host
        # 如果host为空，则默认为本机IP
        server = WebsocketServer(port=8551, host='127.0.0.1')

        threading.Thread(target = self.notify_users,args = (server,), daemon=True).start()


        # 设置当有新客户端接入时的动作
        server.set_fn_new_client(self.new_client)
        # 设置当有客户端断开时的动作
        server.set_fn_client_left(self.client_left)
        # 设置当接收到某个客户端发送的消息后的操作
        server.set_fn_message_received(self.message_back)
        # 设置服务一直运行
        server.run_forever()



    # async def notify_users(self):
    #     try:
    #         while True:
    #             data = self.get_packet()
    #             log.error(data)
    #             await asyncio.sleep(5)
    #             # if self.__users: # asyncio.wait doesn't accept an empty list
    #             #     log.info(data)
    #             #     message = json.dumps(data)
    #             #     await asyncio.wait([user.send(message) for user in self.__users])

    #             # for f in file_name:
    #             #     # 對註冊列表內的客戶端進行推送
    #             #     if self.__users:  # asyncio.wait doesn't accept an empty list
    #             #         # message = "XXXXXXXXXXXXXXXXXXXXXXXX"
    #             #         message = {"image":os.path.join(file_path,f)}
    #             #         message = json.dumps(message)
    #             #         log.info(message)
    #             #         await asyncio.wait([user.send(message) for user in self.__users])
    #             #     time.sleep(3)
    #     except Exception as e:
    #         log.error("notify users error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
    #         return False

    # async def register(self,websocket):
    #     try:
    #         self.__users.add(websocket)
    #         self.set_users(self.__users)
    #         log.info("register user: {}".format(websocket))
    #     except Exception as e:
    #         log.error("register error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
    #         return False

    # async def unregister(self,websocket):
    #     try:
    #         self.__users.remove(websocket)
    #         self.set_users(self.__users)
    #         log.info("unregister user: {}".format(websocket))
    #     except Exception as e:
    #         log.error("unregister error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
    #         return False

    # async def receptionist(self,websocket):
    #     try:
    #         while True:
    #             log.error("ping")
    #             hb_response = None
    #             hb_response = await asyncio.wait_for(websocket.recv(),100)
    #             try:
    #                 log.error(hb_response)
    #             except:
    #                 raise Exception("Heartbeat break down")
    #             # await asyncio.sleep(5)
    #         # try:
    #         #     # 處理客戶端數據請求
    #         #     async for message in websocket:
    #         #         log.info("{}: {}".format(websocket,message))
    #         #         # await websocket.send("hello")
    #         # finally:
    #         #     await self.unregister(websocket)
    #     except Exception as e:
    #         log.error("receptionist error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
    #         return False

    # async def task(self,websocket, path):
    #     try:
    #         async for message in websocket:
    #             await self.register(websocket)
    #             task_receptionist = asyncio.create_task(self.receptionist(websocket))
    #             task_notify = asyncio.create_task(self.notify_users())
    #             await asyncio.gather(task_receptionist,task_notify)

    #             # task_echo = asyncio.create_task(echo(websocket))
    #             # task_notify = asyncio.create_task(notify(websocket))
    #             # await asyncio.gather(task_echo, task_notify)
    #     except Exception as e:
    #         log.error("task error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
    #         return False

    # def launch_server(self):
    #     try:
    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)
    #         ws_server = websockets.serve(self.task, 'localhost', 8551)
    #         loop.run_until_complete(ws_server)
    #         loop.run_forever()
    #         loop.close()
    #     except Exception as e:
    #         log.error("launch server error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
    #         return False

    def register_IPC_server_thread(self):
        try:
            log.info("Register IPC server thread")
            threading.Thread(target = self.launch_server, daemon=True).start()
        except Exception as e:
            log.error("Register IPC server thread error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False


# if __name__ == '__main__':

#     instance = IPC_server()
#     threading.Thread(target=instance.launch_server, daemon=True).start()

#     while True:
#         log.info("heartbeats")
#         time.sleep(600)




# import setproctitle

# def run():
#     setproctitle.setproctitle("digital_signage")





# 通訊協定(websocket/ socket???) 選一個