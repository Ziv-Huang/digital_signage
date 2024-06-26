import os
import sys
import numpy
# import cv2
import time
import pandas
import xlrd
import traceback
import threading
import getpass
from enum import Enum
from loguru import logger as log

# Same name as the system image
class STATUS(Enum):
    UPDATING = "updating"
    DEFAULT = "default"
    FAIL = "fail"

class JS_FUNC:
    load_gif = "load_gif"
    load_image = "load_image"
    load_video = "load_video"
    display_gif = "display_gif"
    display_image = "display_image"
    display_video = "display_video"
    display_camera = "display_camera"
    update_text = "update_text"

class player:

    def __init__(self,ipc_instance):
        self.SET_WAIT_TIME = 0.01
        self.__ipc_instance = ipc_instance
        self.run_path = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
        self.excel_setting = None
        self.media = None
        self.show_time = None
        #self.screen = None
        self.usb_media_folder = "宏碁廣告投放"
        self.sheet_name = "廣告"
        self.excel_file_name = "info.xlsx"
        self.excel_path = "%s/media/%s" % (self.run_path, self.excel_file_name)
        self.excel_setting = self.read_excel_setting(self.excel_path)
        self.update_status = STATUS.FAIL

    def load_media(self):
        try:
            log.info("load media")
            data = {
                        "command":None,
                        "data":{
                            "name":None,
                            "src":None
                        }
                    }

            ### system
            data["command"] = JS_FUNC.load_image
            for i in os.listdir("image"):
                name = i[:i.find(".")]
                data["data"]["name"] = name
                data["data"]["src"] = "%s/image/%s" % (self.run_path, i)
                self.__ipc_instance.set_packet(data)
                time.sleep(self.SET_WAIT_TIME)

            ### ad
            status_flag = True
            for idx, item in enumerate(self.excel_setting):
                file_path = "%s/media/%s" % (self.run_path, self.excel_setting[idx][0])
                if not os.path.isfile(file_path):
                    log.error("Media File \"%s\" Not Found In \"%s/media\" Folder" % (self.excel_setting[idx][0], self.run_path))
                    status_flag = False
                    break
                data["data"]["name"] = self.excel_setting[idx][0]
                data["data"]["src"] = file_path
                if self.excel_setting[idx][0].find(".mp4") >= 0:
                    data["command"] = JS_FUNC.load_video
                    self.__ipc_instance.set_packet(data)
                    time.sleep(self.SET_WAIT_TIME)
                elif self.excel_setting[idx][0].find(".jpg") >= 0 or self.excel_setting[idx][0].find(".png") >= 0:
                    data["command"] = JS_FUNC.load_image
                    self.__ipc_instance.set_packet(data)
                    time.sleep(self.SET_WAIT_TIME)
                else:
                    status_flag = False

            if status_flag == False:
                self.update_status = STATUS.FAIL
            else:
                self.update_status = STATUS.DEFAULT

        except Exception as e:
            log.error("load ad error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def read_excel_setting(self, excel_path):
        excel_setting = []
        if os.path.isfile(excel_path):
            try:
                df = pandas.read_excel(excel_path, sheet_name = self.sheet_name)
                sheet = self.sheet_name
            except Exception as e:
                if type(e) == xlrd.biffh.XLRDError:
                    log.warning("Not Found Sheet Name of \"廣告\", Read default Sheet")
                    df = pandas.read_excel(excel_path)
                    xls = pandas.ExcelFile(excel_path)
                    sheet_list = xls.sheet_names
                    log.info("Sheet List: %s" % sheet_list)
                    sheet = sheet_list[0]

            data = pandas.read_excel(excel_path, sheet)
            #log.info(data)
            collist = df.columns
            log.info("Total %d Advertisement" % df.shape[0])
            for row in range(df.shape[0]):
                one_row = df.iloc[row,:]
                file_name = one_row[0]
                if not numpy.isnan(one_row[1]).any():
                    play_time = int(one_row[1])
                else:
                    play_time = None
                excel_setting.append([file_name, play_time])
        else:
            log.error("Not Found Excel File In %s" % excel_path)
        return excel_setting

    def check_media_file_exist(self, usb_media_folder_path):
        log.info("Check Media Files is Exist in USB Device")
        result = False

        # Check Folder Content
        if os.path.isfile("%s/%s" % (usb_media_folder_path, self.excel_file_name)):
            excel_setting = self.read_excel_setting("%s/%s" % (usb_media_folder_path, self.excel_file_name))
            usb_files = os.listdir(usb_media_folder_path)
            file_not_exist = False
            for item in excel_setting:
                if item[0] not in usb_files:
                    file_not_exist = True
                    break
            if file_not_exist:
                log.warning("Have Media File Not in USB Device")
            else:
                log.info("Check Media File Pass")
                result = True

        return result

    def change_media_files(self, usb_media_folder_path):
        log.info("Prepare Update Media Files")

        if os.path.isfile("%s/%s" % (usb_media_folder_path, self.excel_file_name)):
            log.info("Start Update Midea Files")
            #self.updating = True
            self.media = None
            time.sleep(5)
            result = os.system("rm -rf %s/media/*" % self.run_path)
            time.sleep(5)
            if result == 0:
                result = os.system("cp %s/* %s/media" % (usb_media_folder_path, self.run_path))
                if result == 0:
                    log.info("Update Media Files Success")
                    self.excel_setting = self.read_excel_setting(self.excel_path)
                    time.sleep(5)
                    self.updating = False
                    self.media = None
                    log.info("#### Stop Update Image ####")
                else:
                    log.error("Update Media Files Fail")
            else:
                log.error("Delete Old Media Files Fail")
        else:
            log.warning("Not Found \"%s\" File" % self.excel_file_name)

    def detect_usb_connect(self):
        user_name = getpass.getuser()
        detected = False
        while True:
             if self.stop_update_thread:
                 break
             else:
                 array = os.listdir("/media/%s" % user_name)
                 if len(array) == 0:
                     #log.warning("Not Found USB Device")
                     detected = False
                 elif (len(array) == 1) and (not detected):
                     log.info("### Found One USB Device ###")
                     detected = True
                     time.sleep(5)
                     usb_media_folder_path = "/media/%s/%s/%s" % (user_name, array[0], self.usb_media_folder)
                     if os.path.isdir(usb_media_folder_path):
                         log.info("Found \"%s\" Folder In USB Device" % self.usb_media_folder)
                         self.updating = True
                         # Check Folder Content
                         array = os.listdir(usb_media_folder_path)
                         if len(array) == 0:
                             log.warning("Not Found Any Files in %s" % usb_media_folder_path)
                         else:
                             result = self.check_media_file_exist(usb_media_folder_path)
                             if result:
                                 self.change_media_files(usb_media_folder_path)
                             else:
                                 self.update_fail = True
                                 time.sleep(5)
                                 self.excel_setting = self.read_excel_setting(self.excel_path)
                                 time.sleep(5)
                                 self.update_fail = False
                                 self.media = None
                     else:
                         log.warning("Not Found \"%s\" Folder" % self.usb_media_folder)
                 elif len(array) >= 2:
                     log.warning("Found More Than One USB Devices")
                     detected = False
             time.sleep(1)

    def play_ad(self):
        try:
            data = {
                    "command":None,
                    "data":{
                        "name":None
                    }
                }
            if self.__ipc_instance.get_users():
                self.load_media()
            while True:
                wait_ad_time = 3 ### test ###
                data["command"] = JS_FUNC.display_image
                if self.update_status != STATUS.DEFAULT:
                    data["data"]["name"] = self.update_status.name
                    self.__ipc_instance.set_packet(data)
                    time.sleep(self.SET_WAIT_TIME)
                    time.sleep(wait_ad_time)
                else:
                    for item in self.excel_setting:
                        if item[0].find("mp4") >= 0:
                            data["command"] = JS_FUNC.display_video
                            data["data"]["name"] = item[0]
                            self.__ipc_instance.set_packet(data)
                            time.sleep(self.SET_WAIT_TIME)
                            video_end_flag = self.__ipc_instance.get_video_end()
                            while not video_end_flag:
                                video_end_flag = self.__ipc_instance.get_video_end()

                        elif item[0].find("jpg") >= 0 or item[0].find("png") >= 0:
                            data["command"] = JS_FUNC.display_image
                            data["data"]["name"] = item[0]
                            self.__ipc_instance.set_packet(data)
                            time.sleep(self.SET_WAIT_TIME)
                        if type(item[1]) == int:
                            wait_ad_time = int(item[1])
                            time.sleep(wait_ad_time)

        except Exception as e:
            log.error("Register player thread error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

    def register_player_thread(self):
        try:
            log.info("Register player thread")
            # threading.Thread(target = self.detect_usb_connect, args=()).start()
            threading.Thread(target = self.play_ad, args=()).start()
        except Exception as e:
            log.error("Register player thread error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

# if __name__ == '__main__':
#     log = log.Logger(level="debug")
#     p = player(log)
#     p.main()