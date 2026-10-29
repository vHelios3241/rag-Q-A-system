from typing import List, Dict, Any

from src.llm import LLM

def generate_answer(
        llm: LLM,
        question: str,
        results: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
    '''
        生成回答
        Args：
            llm: LLM对象
            question: 问题
            results: 检索结果
            temperature: 生成温度
            max_tokens: 生成最大token数
        Returns：
            Dict[str, Any]
    '''
    if not results:
        return {
            'answer': '没有找到相关内容',
            'question': question,
            'content': ""}

    # 格式化上下文

    #构建提示词

    # 调用llm生成回答

    # 返回结果

def format_context(
        results: List[Dict[str, Any]],
        max_char: int = 1500,
    ) -> str:
    '''
        格式化上下文
        Args：
            results: 检索结果
            max_length: 上下文最大长度
        Returns：
            str
    '''
    # 创建去重元组
    seen = set()
    # 存储格式化后的结果
    parts=[]
    # 总长度
    total=0
    # 遍历
    for result in results:
        # 去除空格
        content = result.get('content', '').strip()
        # 如果已经存在，跳过
        if content and content in seen:
            continue

        next_total = total + len(content) + (2 if len(parts) else 0)
        # 如果长度超过，跳过
        if next_total > max_char:
            continue

        # 添加到元组
        seen.add(content)
        # 添加到结果
        parts.append(content)
        # 更新总长度
        total = next_total
        # 如果长度超过，跳过
        if total + len(content) > max_char:
            continue

        # 添加到元组 (记里，防止后续重复)
        seen.add(content)
        # 添加到结果
        parts.append(content)
        # 更新总长度
        total = next_total

    return "\n\n".join(parts)

