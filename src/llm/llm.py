from typing import List, Dict, Any, Optional


from openai import OpenAI

class LLM:
    def __init__(self, 
                 model: str,
                 api_key: str,
                 base_url: str):
            self.model = model
            self.api_key = api_key
            self.base_url = base_url

            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate(self, 
                 messages: List[dict],
                 max_tokens: int = 2000,
                 temperature: float = 0.7,) -> Dict[str, Any]:
            '''
            生成内容
            Args：
              messages: List[dict]  消息列表
              max_tokens: int  最大token数
              temperature: float  温度
            Returns：
              Dict[str, Any]  返回结果
            '''

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            choise = response.choices[0]
            return{
                'content': choise.message.content,
                'finish_reason': choise.finish_reason,
                'token_used':{
                       'total':response.usage.total_tokens,
                       'prompt':response.usage.prompt_tokens,
                       'completion':response.usage.completion_tokens
                },
                'model': self.model
            }