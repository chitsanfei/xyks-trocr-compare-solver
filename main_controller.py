import time
import os
import subprocess
from PIL import Image

class MainController:
    def __init__(self, logger, ocr_manager, input_simulator, answer_calculator, adb_manager):
        self.logger = logger
        self.ocr_manager = ocr_manager
        self.input_simulator = input_simulator
        self.answer_calculator = answer_calculator
        self.adb_manager = adb_manager  # 赋值 adb_manager

    def capture_screenshot(self):
        """
        使用 ADB 捕获设备的屏幕截图，并保存为本地文件。
        """
        try:
            # 使用 ADBManager 中的 adb 路径
            adb_command_screenshot = self.adb_manager.get_adb_command() + ['shell', 'screencap', '-p', '/sdcard/screen.png']
            adb_command_pull = self.adb_manager.get_adb_command() + ['pull', '/sdcard/screen.png', 'screenshot.png']
            
            # 执行截图和拉取图片到本地的命令
            subprocess.run(adb_command_screenshot, check=True)
            subprocess.run(adb_command_pull, check=True)
            
            # 打开截图并返回 PIL 图像对象
            return Image.open('screenshot.png')
        except Exception as e:
            self.logger.log('ERROR', 'MainController: capture_screenshot', f"截图失败: {e}")
            return None

    def run(self):
        try:
            failure_count = 0  # 记录连续OCR失败的次数
            while True:
                # 捕获屏幕截图并裁剪到 ocr_region
                screenshot = self.capture_screenshot()
                if screenshot is None:
                    self.logger.log('ERROR', 'MainController: run', "截屏失败，跳过此次循环。")
                    time.sleep(1)
                    continue

                ocr_result = self.ocr_manager.perform_ocr(screenshot)

                if ocr_result is not None:
                    failure_count = 0  # 重置失败计数
                    num1, num2 = ocr_result  # 解包两个数字
                    self.logger.log('INFO', 'MainController: run', f"OCR 识别到的数字: {num1} 和 {num2}")

                    # 解析表达式，获取两个数字
                    a, b = self.answer_calculator.parse_expression([str(num1), str(num2)])
                    if a is None or b is None:
                        self.logger.log('ERROR', 'MainController: run', "解析表达式失败，跳过此次循环。")
                        time.sleep(1)
                        continue

                    # 根据识别到的数字计算符号，例如 >、<、=
                    symbol = self.answer_calculator.calculate_answer(a, b)
                    if symbol is None:
                        self.logger.log('ERROR', 'MainController: run', "计算符号失败，跳过此次循环。")
                        time.sleep(1)
                        continue

                    # 生成绘制路径并绘制符号
                    path = self.input_simulator.generate_draw_path(symbol)
                    self.input_simulator.draw_symbol(path)
                else:
                    failure_count += 1
                    self.logger.log('ERROR', 'MainController: run', f"OCR 识别失败。连续失败次数: {failure_count}")

                    if failure_count >= 5:  # 例如，当连续失败5次时触发警告
                        self.logger.log('CRITICAL', 'MainController: run', "OCR 识别连续失败，可能存在系统问题。")
                        break  # 停止程序或触发其它机制
                
                time.sleep(1)  # 循环间隔

        except (KeyboardInterrupt, SystemExit):
            self.logger.log('INFO', 'MainController: run', "程序被手动终止。")
        except Exception as e:
            self.logger.log('CRITICAL', 'MainController: run', f"运行时发生未处理的错误: {e}")
            raise