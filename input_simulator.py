import subprocess
import time
import random

class InputSimulator:
    """
    模拟触摸输入，绘制符号。
    """
    def __init__(self, region, logger, adb_manager, draw_settings):
        """
        初始化输入模拟器。

        :param region: 输入区域字典，包含x, y, width, height
        :param logger: FormattedLogger实例，用于记录日志
        :param adb_manager: ADBManager实例，用于获取adb命令
        :param draw_settings: 绘制设置字典，包含base_symbol_size和scale_factor
        """
        self.region = region
        self.logger = logger
        self.adb_manager = adb_manager
        self.draw_settings = draw_settings
        self.adb_command = self.adb_manager.get_adb_command()
        self.logger.log('DEBUG', 'InputSimulator: __init__', f"ADB命令: {' '.join(self.adb_command)}")
        self.logger.log('DEBUG', 'InputSimulator: __init__', f"绘制设置: {self.draw_settings}")

    def generate_draw_path(self, symbol):
        """
        根据符号生成绘制路径，并根据配置动态调整符号的大小。

        :param symbol: 要绘制的符号（'>', '<', '='）
        :return: 绘制路径列表
        """
        base_width = self.draw_settings['base_symbol_size']['width']
        base_height = self.draw_settings['base_symbol_size']['height']
        scale_factor = self.draw_settings.get('scale_factor', 1.0)

        scaled_width = base_width * scale_factor
        scaled_height = base_height * scale_factor

        center_x = self.region['x'] + self.region['width'] / 2
        center_y = self.region['y'] + self.region['height'] / 2

        paths = {
            '>': [
                (center_x - scaled_width / 2, center_y - scaled_height / 2),
                (center_x + scaled_width / 2, center_y),
                (center_x - scaled_width / 2, center_y + scaled_height / 2)
            ],
            '<': [
                (center_x + scaled_width / 2, center_y - scaled_height / 2),
                (center_x - scaled_width / 2, center_y),
                (center_x + scaled_width / 2, center_y + scaled_height / 2)
            ],
            '=': [
                (center_x - scaled_width / 2, center_y - scaled_height / 4),
                (center_x + scaled_width / 2, center_y - scaled_height / 4),
                (center_x - scaled_width / 2, center_y + scaled_height / 4),
                (center_x + scaled_width / 2, center_y + scaled_height / 4)
            ]
        }

        if symbol not in paths:
            self.logger.log('ERROR', 'InputSimulator: generate_draw_path', f"无效的符号: {symbol}")
            return []

        return paths[symbol]

    def apply_random_offset(self, point, max_offset=5):
        """
        对给定点加入随机扰动，max_offset 控制最大扰动值。

        :param point: 原始点 (x, y)
        :param max_offset: 最大扰动范围
        :return: 带有扰动的新点 (x, y)
        """
        x, y = point
        x_offset = random.randint(-max_offset, max_offset)
        y_offset = random.randint(-max_offset, max_offset)
        return (x + x_offset, y + y_offset)

    def draw_symbol(self, path):
        """
        根据路径绘制符号，通过 adb swipe 实现连线，并对路径加入扰动。
        """
        try:
            if len(path) < 2:
                self.logger.log('ERROR', 'InputSimulator: draw_symbol', "绘制路径长度不足，无法绘制连线。")
                return

            # 遍历路径中的点，依次用 swipe 进行连接，并加入随机扰动
            for i in range(len(path) - 1):
                start_point = self.apply_random_offset(path[i])
                end_point = self.apply_random_offset(path[i + 1])
                
                adb_command = self.adb_command + ['shell', 'input', 'swipe',
                                                  str(start_point[0]), str(start_point[1]),
                                                  str(end_point[0]), str(end_point[1]), '100']  # 100ms 滑动时间
                subprocess.run(adb_command, check=True)

            self.logger.log('INFO', 'InputSimulator: draw_symbol', f"符号绘制成功: {path}")
        except subprocess.CalledProcessError as e:
            self.logger.log('ERROR', 'InputSimulator: draw_symbol', f"绘制符号时发生错误: {e}")