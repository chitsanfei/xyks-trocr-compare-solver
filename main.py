# main.py
from config_manager import ConfigManager
from adb_manager import ADBManager
from formatted_logger import FormattedLogger
from ocr_manager import OCRManager
from input_simulator import InputSimulator
from answer_calculator import AnswerCalculator
from main_controller import MainController

def main():
    # 初始化日志记录器
    logger = FormattedLogger()

    # 加载配置
    config = ConfigManager.load_or_create_config()

    # 初始化 ADBManager
    adb_address = config.get('adb_address', '127.0.0.1:16384')  # 从配置中读取 ADB 地址
    adb_manager = ADBManager(logger, adb_address)

    # 初始化 OCRManager
    ocr_manager = OCRManager(logger, config)

    # 初始化 AnswerCalculator
    answer_calculator = AnswerCalculator(logger)

    # 初始化 InputSimulator，传递 draw_settings
    draw_settings = config.get('draw_settings', {
        "base_symbol_size": {
            "width": 100,
            "height": 100
        },
        "scale_factor": 1.5
    })
    input_simulator = InputSimulator(config['input_region'], logger, adb_manager, draw_settings)

    # 传递 adb_manager 初始化 MainController
    main_controller = MainController(logger, ocr_manager, input_simulator, answer_calculator, adb_manager)

    # 运行主循环
    main_controller.run()

if __name__ == "__main__":
    main()