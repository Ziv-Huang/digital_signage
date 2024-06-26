import sys
import os
from datetime import datetime
from loguru import logger
from pathlib import Path

class LogInitialization:
    def __init__(self,_level="INFO"):
        project_path = Path.cwd()
        self.log_path = Path(project_path, "LOG")
        self.error_log_path = Path(project_path, "ERROR_LOG")

        logger.remove()
        logger.add(sys.stderr
                    ,level=_level
                    ,format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <level>[{level}] [{file.name}:{line}]: {message}</level>"
                    ,enqueue=True)

        logger.add("{}/record.log".format(self.log_path)
                    ,level=_level
                    ,format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <level>[{level}] [{file.name}:{line}]: {message}</level>"
                    ,rotation="00:00"
                    ,encoding="utf-8"
                    ,retention="1 months"
                    ,enqueue=True)

        logger.add("{}/MRTPF_Error.log".format(self.error_log_path)
                    ,level= "ERROR"
                    ,format="<green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green> - <level>{level}: [{file.name}:{line}] - {message}</level>"
                    ,compression=self.rename_error_log
                    ,rotation="5 minutes"
                    ,encoding="utf-8"
                    ,retention="3 days"
                    ,enqueue=True)

    def rename_error_log(self,filepath):
        now = datetime.strftime(datetime.now(),'%Y-%m-%d_%H:%M:%S')
        os.rename(filepath, "{}/MRTPF_Error_{}.log".format(self.error_log_path,now))




# if __name__ == "__main__":
#     LogInitialization()
#     logger.info("info")
#     logger.debug("debug")
#     logger.warning("warning")
#     logger.error("error")