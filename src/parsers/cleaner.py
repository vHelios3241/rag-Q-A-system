import re


class TextCleaner:
    """文本清理器"""

    # 初始化
    def __init__(self, custom_patterns: list[str] = None):
        '''
        Args:
            custom_patterns (list[str]): 自定义的正则表达式模式列表,默认用于清理文本中的特殊字符、HTML标签等
        '''

        # 常见的无意义模式
        self.patterns_to_remove = [
            r'^\s*\d+\s*$',        # 单独的页码
            r'^\s*[-=_]+\s*$',      # 分隔线
            r'^\s*第\s*\d+\s*页\s*$',   # 中文页码标记
            r'^\s*Page\s*\d+\s*$',    # 英文页码
            r'^\s*\d+\s*/\s*\d+\s*$',   # 页码格式：1/10
        ]

        # 添加自定义模式
        if custom_patterns:
            self.patterns_to_remove.extend(custom_patterns)



    # 清理文本
    def clean(self, text: str) -> str:
        '''
        清洗文本,去除无意义内容
        Args:
            text: 需要清理的文本
        Returns:
            清理后的文本
        '''
        # 1. 对于换行\n，正常换行
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # 跳过空行
            if not line.strip():
                continue

            # 检测是否包含无意义模式
            is_noise = any(re.search(pattern, line) for pattern in self.patterns_to_remove)

            # 如果不包含无意义模式，则添加到清理后的文本中
            if not is_noise:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)



    def normalize_whitespace(self, text: str) -> str:
        '''
        规范化文本中的空白字符
        - 合并多个空格
        - 合并多个换行
        - 去除行首行尾的空白字符

        Args:
            text: 需要规范化的文本
        Returns:
            规范化的文本
        '''
        # 合并多个空格
        text = re.sub(r'\s+', ' ', text)
        # 合并多个换行
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        return text.strip()



    def remove_extra_chars(self, text: str, chars: str = None) -> str:
        '''
        移除多余的特定字符

        Args:
            text: 原始文本
            chars: 要移除的字符，默认为常见的特殊符号

        Returns:
            处理后的文本
        '''
        if chars is None:
            chars = '\u200b\u200c\u200d\ufeff'    # 零宽字符等
            return text.translate(str.maketrans('', '', chars))



    def full_clean(self, text: str) -> str:
        """
        执行完整清洗流程

        Args:
            text: 原始文本

        Returns:
            完全清洗后的文本
        """
        text = self.clean(text)
        text = self.normalize_whitespace(text)
        text = self.remove_extra_chars(text)
        return text