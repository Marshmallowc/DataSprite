import aiohttp
import json
from typing import List, Dict
import warnings

class DeepSeekClient:
    def __init__(self, api_key: str, use_mock: bool = True):
        self.api_key = api_key
        self.use_mock = use_mock
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    async def generate_sku_content(
        self, 
        columns: List[str], 
        prompt: str, 
        num_rows: int
    ) -> List[Dict[str, str]]:
        # 如果使用模拟模式
        if self.use_mock:
            warnings.warn("使用模拟数据模式，返回测试数据。")
            # 生成模拟数据
            mock_data = []
            for i in range(num_rows):
                row = {}
                for col in columns:
                    if col == "身高":
                        row[col] = f"{160 + i * 5}cm"
                    elif col == "体重":
                        row[col] = f"{50 + i * 3}kg"
                    elif col == "年龄":
                        row[col] = f"{18 + i}岁"
                    elif col == "性格":
                        personalities = ["开朗", "内向", "活泼", "稳重", "热情"]
                        row[col] = personalities[i % len(personalities)]
                    elif col == "性别":
                        row[col] = "男" if i % 2 == 0 else "女"
                    else:
                        row[col] = f"测试数据_{col}_{i + 1}"
                mock_data.append(row)
            return mock_data
            
        # 构建提示词
        system_prompt = (
            f"你是一个SKU生成助手。请根据以下列名生成{num_rows}行数据，"
            f"返回JSON格式的数组，每个对象包含这些列名作为key：{columns}\n"
            f"要求：\n"
            f"1. 生成的内容要符合实际情况\n"
            f"2. 数据要多样化，避免重复\n"
            f"3. 严格按照JSON格式返回，不要包含其他说明文字"
        )
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                
                # 添加调试信息
                print(f"发送请求到: {self.api_url}")
                print(f"请求头: {self.headers}")
                print(f"请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    ssl=True
                ) as response:
                    response_text = await response.text()
                    print(f"API响应: {response_text}")
                    
                    if response.status != 200:
                        error_msg = f"API调用失败 (状态码: {response.status}): {response_text}"
                        print(f"错误详情: {error_msg}")
                        raise Exception(error_msg)
                    
                    result = json.loads(response_text)
                    try:
                        content = result["choices"][0]["message"]["content"]
                        return json.loads(content)
                    except (KeyError, json.JSONDecodeError) as e:
                        raise Exception(f"解析API响应失败: {str(e)}")
        except Exception as e:
            raise Exception(f"调用DeepSeek API时发生错误: {str(e)}") 