import threading
import asyncio
import websockets
import time
import os
import json

class JS_FUNC:
    load_gif = "load_gif"
    load_image = "load_image"
    load_video = "load_video"
    display_gif = "display_gif"
    display_image = "display_image"
    display_video = "display_video"
    display_camera = "display_camera"
    update_text = "update_text"


class ad_server:
    def __init__(self):
        self.users = set()
        self.data = None

    async def notify_users(self):
        ########
        這裡處理對應的動作透過json

        file_path = "../../media"
        file_name = ["test1.png","test2.png"]
        

        while True:
            for f in file_name:
                # 對註冊列表內的客戶端進行推送
                if self.users:  # asyncio.wait doesn't accept an empty list
                    # message = "XXXXXXXXXXXXXXXXXXXXXXXX"
                    message = {"image":os.path.join(file_path,f)}
                    message = json.dumps(message)
                    print(message)
                    await asyncio.wait([user.send(message) for user in self.users])
                time.sleep(3)

    async def register(self,websocket):
        self.users.add(websocket)
        print("register user: {}".format(websocket))

    async def unregister(self,websocket):
        self.users.remove(websocket)
        print("unregister user: {}".format(websocket))

    async def receptionist(self,websocket):
        await self.register(websocket)
        try:
            # 處理客戶端數據請求
            async for message in websocket:
                print(websocket,message)
                # await websocket.send("hello")
        finally:
            await self.unregister(websocket)

    async def task(self,websocket, path):
        
        task_receptionist = asyncio.create_task(self.receptionist(websocket))
        task_notify = asyncio.create_task(self.notify_users())
        await asyncio.gather(task_receptionist,task_notify)

        # task_echo = asyncio.create_task(echo(websocket))
        # task_notify = asyncio.create_task(notify(websocket))
        # await asyncio.gather(task_echo, task_notify)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ws_server = websockets.serve(self.task, 'localhost', 8765)
        loop.run_until_complete(ws_server)
        loop.run_forever()
        loop.close()

if __name__ == '__main__':

    instance = ad_server()
    threading.Thread(target=instance.run, daemon=True).start()

    while True:
        print("heartbeats")
        time.sleep(600)




# import setproctitle

# def run():
#     setproctitle.setproctitle("digital_signage")





# 通訊協定(websocket/ socket???) 選一個