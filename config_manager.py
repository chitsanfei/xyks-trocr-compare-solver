import json
import os

class ConfigManager:
    """
    负责加载和生成配置文件，默认设置为屏幕900x1600分辨率和DPI 320，
    允许设置自定义的ADB地址，默认ADB地址为127.0.0.1:16384。
    上半部分用于OCR识别，下半部分用于输入。
    """
    CONFIG_PATH = './config/config.json'

    @staticmethod
    def load_or_create_config():
        """
        加载现有配置或生成默认配置文件。如果目录不存在，则自动创建目录。
        """
        config_dir = os.path.dirname(ConfigManager.CONFIG_PATH)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        try:
            if os.path.exists(ConfigManager.CONFIG_PATH):
                with open(ConfigManager.CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = ConfigManager.generate_default_config()
                with open(ConfigManager.CONFIG_PATH, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
            return config
        except Exception as e:
            raise RuntimeError(f"配置加载或生成失败: {e}")

    @staticmethod
    def generate_default_config():
        """
        默认生成900x1600分辨率和DPI 320的配置，ADB地址默认为127.0.0.1:16384，
        使用 HuggingFace 的 TrOCR 进行 OCR 识别。
        上半部分用于OCR识别，下半部分用于输入。
        """
        config = {
            "screen_width": 900,
            "screen_height": 1600,
            "dpi": 320,
            "ocr_region": {
                "digit1": {
                    "x": 258,
                    "y": 410,
                    "width": 140,
                    "height": 102
                },
                "digit2": {
                    "x": 516,
                    "y": 410,
                    "width": 110,
                    "height": 102
                }
            },
            "input_region": {
                "x": 250,
                "y": 1000,
                "width": 400,
                "height": 300
            },
            "adb_address": "127.0.0.1:16384",
            "draw_settings": {
                "base_symbol_size": {
                    "width": 100,
                    "height": 100
                },
                "scale_factor": 1.5  // 可以根据需要调整
            }
        }
        return config

    @staticmethod
    def get_adb_address(config):
        """
        从配置文件获取ADB地址。
        """
        return config.get("adb_address", "127.0.0.1:16384")

    @staticmethod
    def get_screen_size(config):
        """
        获取屏幕的分辨率和DPI。
        """
        screen_width = config.get("screen_width", 900)
        screen_height = config.get("screen_height", 1600)
        dpi = config.get("dpi", 320)
        return screen_width, screen_height, dpi
