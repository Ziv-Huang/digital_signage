import os
import sys
import numpy
import datetime
import time
import pandas
import xlrd
import signal
import traceback
import threading
import getpass
#import screeninfo
from loguru import logger as log

class player:

    def __init__(self,ipc_instance):
        self.__ipc_instance = ipc_instance
        self.run_path = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
        self.now_idx = 0
        self.excel_setting = None
        self.media_player = None
        self.media = None
        self.show_time = None
        #self.screen = None
        self.usb_media_folder = "宏碁廣告投放"
        self.sheet_name = "廣告"
        self.excel_file_name = "info.xlsx"
        self.excel_path = "%s/media/%s" % (self.run_path, self.excel_file_name)
        self.updating = False
        self.default = False
        self.update_fail = False
        #self.do_default = False
        #self.do_update_fail = False
        self.stop_update_thread = False
        self.stop_play_video = False

    def init_vlc(self):
        instance = vlc.Instance("--no-xlib")
        instance.log_unset()
        self.media_player = vlc.MediaPlayer(instance)
        self.media_player.toggle_fullscreen()

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
                log.info("  - %s : %s(sec)" % (file_name, play_time))
        else:
            log.error("Not Found Excel File In %s" % excel_path)

        return excel_setting

    def get_media_source(self):
        if self.updating:
            print ("#### Play Update Image ####")
            self.show_time = "system"
            self.media = vlc.Media("%s/image/updating.png" % self.run_path)
            self.media_player.set_media(self.media)
            self.media_player.play()
            time.sleep(2)
            self.default = False
            self.update_fail = False
        elif self.default:
            print ("#### Play Default Image ####")
            self.show_time = "system"
            self.media = vlc.Media("%s/image/default.png" % self.run_path)
            self.media_player.set_media(self.media)
            self.media_player.play()
            time.sleep(2)
        elif self.update_fail:
            print ("#### Play Fail Image ####")
            self.show_time = "system"
            self.media = vlc.Media("%s/image/fail.png" % self.run_path)
            self.media_player.set_media(self.media)
            self.media_player.play()
            time.sleep(2)
        else:
            self.get_ad_source()

    def get_ad_source(self):
        done = False
        for idx, item in enumerate(self.excel_setting):
            if self.now_idx == idx:
                file_path = "%s/media/%s" % (self.run_path, self.excel_setting[idx][0])
                if self.excel_setting[idx][0].find(".mp4") >= 0:
                    if os.path.isfile(file_path):
                        self.media = vlc.Media(file_path)
                        self.show_time = None
                        self.media_player.set_media(self.media)
                        self.media_player.play()
                        log.info("Play Video File: %s" % self.excel_setting[idx][0])
                        print ("#### Play Video ####")
                        time.sleep(2)
                        done = True
                    else:
                        self.media = None
                        log.error("Video File \"%s\" Not Found In \"%s/media\" Folder" % (self.excel_setting[idx][0], self.run_path))
                    break
                else:
                    if os.path.isfile(file_path):
                        self.media = vlc.Media(file_path)
                        self.show_time = self.excel_setting[idx][1]
                        self.media_player.set_media(self.media)
                        self.media_player.play()
                        log.info("Play Image File: %s" % self.excel_setting[idx][0])
                        print ("#### Play Image ####")
                        time.sleep(2)
                        done = True
                    else:
                        self.media = None
                        log.error("Image File \"%s\" Not Found In \"%s/media\" Folder" % (self.excel_setting[idx][0], self.run_path))
                    break
        if not done:
            if len(self.excel_setting) == 0:
                self.default = True
            else:
                self.update_fail = True
        else:
            self.default = False
            self.update_fail = False

        if len(self.excel_setting) == self.now_idx + 1:
            self.now_idx = 0
        else:
            self.now_idx += 1

    def play_video(self):
        start_time = None
        duration_time = 0

        while not self.stop_play_video:
            now_time = datetime.datetime.utcnow()+datetime.timedelta(hours=8)

            if self.media is None:
                self.get_media_source()
            else:
                value = self.media_player.is_playing()
                if (value == 0) and (self.show_time is None):
                    print ("#### Finish Stop ####")
                    self.media = None
                else:
                    if (not self.updating) and (not self.default) and (not self.update_fail):
                        if self.show_time is not None:
                            if start_time is None:
                                start_time = now_time
                            else:
                                duration_time = int((now_time - start_time).total_seconds()) + 2
                                print ("Wait %ds ... (%ds)" % (self.show_time, duration_time))
                                if duration_time >= self.show_time:
                                    start_time = None
                                    duration_time = 0
                                    self.media = None
                                    print ("#### Time Stop ####")
                    else:
                        start_time = None
            time.sleep(1)

    """
    def get_media_new_resolution(self, frame):
        width_scale = self.screen[0] / frame.shape[1]
        heigh_scale = self.screen[1] / frame.shape[0]
        if width_scale > heigh_scale:
            scale = heigh_scale
        else:
            scale = width_scale
        width = int(frame.shape[1] * scale)
        heigh = int(frame.shape[0] * scale)

        return (width, heigh)
    """

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
                                 self.now_idx = 0
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
                    self.now_idx = 0
                    self.excel_setting = self.read_excel_setting(self.excel_path)
                    time.sleep(5)
                    self.updating = False
                    self.media = None
                    print ("#### Stop Update Image ####")
                else:
                    log.error("Update Media Files Fail")
            else:
                log.error("Delete Old Media Files Fail")
        else:
            log.warning("Not Found \"%s\" File" % self.excel_file_name)

    def signal_handler(self, signum, frame):
        if self.media_player is not None:
            self.media_player.stop()
        self.stop_update_thread = True
        self.stop_play_video = True

    def main(self):
        log.info("Start Player")
        """
        screen_info = screeninfo.get_monitors()
        if len(screen_info) == 1:
            log.info("Screen Width: %d, Height: %d" % (screen_info[0].width, screen_info[0].height))
            self.screen = (screen_info[0].width, screen_info[0].height)
        else:
            self.screen = (1920, 1080)
        """
        signal.signal(signal.SIGINT, self.signal_handler)
        self.init_vlc()
        self.excel_setting = self.read_excel_setting(self.excel_path)
        self.get_media_source()

        update_thread = threading.Thread(target = self.detect_usb_connect, args=())
        update_thread.start()

        self.play_video()

    def register_player_thread(self):
        try:
            log.info("Register player thread")
            threading.Thread(target = self.main, daemon=True).start()
        except Exception as e:
            log.error("Register player thread error: {}, {}".format(e,traceback.format_exc(limit=1,chain=False)))
            return False

# if __name__ == '__main__':
#     log = log.Logger(level="debug")
#     p = player(log)
#     p.main()