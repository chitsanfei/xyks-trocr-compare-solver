import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class FormattedLogger:
    """
    配置和管理日志记录，输出格式为 “[时间](类名: 方法名)提示”，并使用不同颜色显示时间和类名:方法名。
    """
    LOG_PATH = './logs/app.log'

    COLOR_TIME = '\033[94m'
    COLOR_CLASS_METHOD = '\033[92m'
    COLOR_RESET = '\033[0m'

    def __init__(self):
        os.makedirs(os.path.dirname(FormattedLogger.LOG_PATH), exist_ok=True)
        self.logger = logging.getLogger('AutoMathApp')
        self.logger.setLevel(logging.DEBUG)

        # 创建文件处理器，设置最大日志大小为5MB，保留3个旧日志文件
        fh = RotatingFileHandler(FormattedLogger.LOG_PATH, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def log(self, level, class_method, message):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"{self.COLOR_TIME}[{current_time}]{self.COLOR_RESET} " \
                            f"{self.COLOR_CLASS_METHOD}({class_method}){self.COLOR_RESET} {message}"

        if level == 'DEBUG':
            self.logger.debug(formatted_message)
        elif level == 'INFO':
            self.logger.info(formatted_message)
        elif level == 'WARNING':
            self.logger.warning(formatted_message)
        elif level == 'ERROR':
            self.logger.error(formatted_message)
        elif level == 'CRITICAL':
            self.logger.critical(formatted_message)