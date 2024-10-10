class AnswerCalculator:
    """
    解析表达式并计算正确的符号。
    """
    def __init__(self, logger):
        """
        初始化答案计算器。

        :param logger: FormattedLogger实例，用于记录日志
        """
        self.logger = logger

    def parse_expression(self, digits):
        """
        解析OCR识别到的数字列表。

        :param digits: 数字列表，例如 ['3', '2']
        :return: a, b
        """
        try:
            if isinstance(digits, list) and len(digits) >= 2 and all(isinstance(d, str) and d.isdigit() for d in digits):
                a, b = int(digits[0]), int(digits[1])
                self.logger.log('DEBUG', 'AnswerCalculator: parse_expression', f"解析表达式: {a} 和 {b}")
                return a, b
            else:
                self.logger.log('ERROR', 'AnswerCalculator: parse_expression', f"无法解析表达式: {digits}")
                return None, None
        except Exception as e:
            self.logger.log('ERROR', 'AnswerCalculator: parse_expression', f"解析表达式时出错: {e}")
            return None, None

    def calculate_answer(self, a, b):
        """
        根据数字比较计算正确的符号。

        :param a: 第一个数字
        :param b: 第二个数字
        :return: 正确的符号（'>'，'<'，'='）
        """
        try:
            if a > b:
                answer = '>'
            elif a < b:
                answer = '<'
            else:
                answer = '='
            self.logger.log('DEBUG', 'AnswerCalculator: calculate_answer', f"计算答案: {a} 和 {b} => {answer}")
            return answer
        except Exception as e:
            self.logger.log('ERROR', 'AnswerCalculator: calculate_answer', f"计算答案时出错: {e}")
            return 'error'
