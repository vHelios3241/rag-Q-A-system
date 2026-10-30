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
    context = format_context(results)

    #构建提示词
    prompt = build_prompt(question, context)

    # 调用llm生成回答
    messages = [{'role': 'user', 'content': prompt}] 
    answer = llm.generate(
        messages,
        temperature=temperature,
        max_tokens=max_tokens)
    
    # 返回结果
    return {
        'answer': answer.get('content', ''),
        'question': question,
        'content': context,
        'tokens': answer['token_used'],
        'model': answer['model'],
        }


def build_prompt(question: str, context: str) -> str:
    """
    构建提示词
    Args:
        question: 问题
        context: 上下文
    Returns:
        str: 提示词
    """
    # 提示词要求：
    instrution = (
        '你是一个基于文档的问答助手，请严格依据上下文回答问题：'
        '如果上下文缺失相关信息，请回答“不知道”。'
    )
    return (
        f'{instrution}\n\n'
        f'[上下文]\n{context}\n\n'
        f'[问题]\n问:{question}\n答:'
    )

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

