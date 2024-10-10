from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image, ImageEnhance, ImageFilter
import torch
import re
from concurrent.futures import ThreadPoolExecutor

class OCRManager:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        # 初始化 OCR 模型
        self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-stage1')
        self.model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-stage1')

        # 如果有 GPU 可用，使用 GPU 并启用半精度推理
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # 如果使用 GPU，启用半精度以提高性能
        if torch.cuda.is_available():
            self.model = self.model.half()

    def preprocess_image(self, pil_image):
        try:
            # 确保图像为 RGB 模式
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')  # 强制转换为 RGB 模式
                self.logger.log('DEBUG', 'OCRManager: preprocess_image', "图像已转换为 RGB 模式。")

            # 可选的图像增强处理，如锐化或对比度调整
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(2.0)  # 增强对比度
            return pil_image
        except Exception as e:
            self.logger.log('ERROR', 'OCRManager: preprocess_image', f"图像预处理失败: {e}")
            return None

    def process_ocr_region(self, region, preprocessed_image):
        """
        单个OCR区域处理函数，用于并行执行。
        """
        cropped_image = preprocessed_image.crop((
            region['x'], region['y'],
            region['x'] + region['width'], region['y'] + region['height']
        ))

        # 将图像转换为像素值，并确保使用正确的设备（CPU 或 GPU）
        pixel_values = self.processor(images=cropped_image, return_tensors="pt").pixel_values.to(self.device)

        # 如果使用 GPU，确保数据格式与半精度推理匹配
        if torch.cuda.is_available():
            pixel_values = pixel_values.half()

        # 模型推理
        generated_ids = self.model.generate(pixel_values)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return generated_text

    def perform_ocr(self, pil_image):
        try:
            # 在传递给 OCR 模型之前，确保图像已经过预处理
            preprocessed_image = self.preprocess_image(pil_image)
            if preprocessed_image is None:
                self.logger.log('ERROR', 'OCRManager: perform_ocr', "图像预处理失败。")
                return None

            # 获取 ocr_region 配置
            ocr_regions = self.config.get('ocr_region', {})
            if not ocr_regions:
                self.logger.log('ERROR', 'OCRManager: perform_ocr', "配置文件中缺少 'ocr_region'。")
                return None

            # 使用多线程并行处理 OCR 区域
            with ThreadPoolExecutor() as executor:
                ocr_results = list(executor.map(
                    lambda region: self.process_ocr_region(region, preprocessed_image),
                    ocr_regions.values()
                ))

            # 处理OCR结果并提取数字
            numbers = []
            for result in ocr_results:
                digit = re.findall(r'\d+', result)
                if digit:
                    numbers.append(digit[0])
                else:
                    self.logger.log('ERROR', 'OCRManager: perform_ocr', "OCR 结果中未找到数字。")
                    return None

            return numbers if len(numbers) == 2 else None
        except Exception as e:
            self.logger.log('ERROR', 'OCRManager: perform_ocr', f"OCR处理时出错: {e}")
            return None
