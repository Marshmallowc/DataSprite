import aiohttp
import json
from typing import List, Dict
import warnings
from config import SUPPORTED_MODELS, DEFAULT_MODEL
import asyncio
from concurrent.futures import ThreadPoolExecutor
import backoff  # 需要添加到 requirements.txt

class DeepSeekClient:
    def __init__(self, api_key: str, use_mock: bool = True, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.use_mock = use_mock
        self.model = model
        model_config = SUPPORTED_MODELS.get(model, SUPPORTED_MODELS[DEFAULT_MODEL])
        self.api_url = model_config["url"]
        self.model_id = model_config["id"]
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def update_api_key(self, api_key: str):
        """更新API密钥"""
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def update_model(self, model: str):
        """更新模型"""
        if model not in SUPPORTED_MODELS:
            raise ValueError(f"不支持的模型: {model}")
        self.model = model
        model_config = SUPPORTED_MODELS[model]
        self.api_url = model_config["url"]
        self.model_id = model_config["id"]
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=30
    )
    async def _make_api_request(self, session, payload):
        """发送API请求，支持自动重试"""
        async with session.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            ssl=True,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            response_text = await response.text()
            
            if response.status != 200:
                if response.status in [502, 503, 504]:
                    raise aiohttp.ClientError(f"服务器暂时不可用 (状态码: {response.status})")
                raise Exception(f"API调用失败 (状态码: {response.status}): {response_text}")
            
            return response_text
    
    async def generate_sku_content(
        self, 
        columns: List[str], 
        prompt: str, 
        num_rows: int,
        progress_callback=None
    ) -> List[Dict[str, str]]:
        """一次性生成所有SKU数据"""
        if self.use_mock:
            if progress_callback:
                progress_callback("🔄 使用模拟数据模式")
            return self._generate_mock_data(columns, num_rows, progress_callback)
        
        system_prompt = (
            f"你是一个严格的SKU数据生成助手。请按照以下格式生成数据：\n"
            "[\n"
            "  {\n"
            f"    // 第1行数据，必须包含这些列：{columns}\n"
            "  },\n"
            "  {\n"
            f"    // 第2行数据，如此类推，直到第{num_rows}行\n"
            "  }\n"
            "]\n\n"
            f"⚠️ 极其重要的要求：\n"
            f"1. 必须严格生成 {num_rows} 行数据，不能多也不能少\n"
            f"2. 请在生成过程中仔细计数：1,2,3...直到{num_rows}\n"
            f"3. 生成完成后，请再次数一遍确保数量正确\n"
            f"4. 每行数据必须且仅包含这些列：{columns}\n"
            "5. 生成的内容要符合实际情况\n"
            "6. 数据要多样化，避免重复\n"
            "7. 每个值都要有实际意义\n"
            "8. 必须是标准的JSON格式，不要包含任何注释\n"
            "\n请开始生成，记住要一行一行地数..."
        )

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model_id,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,  # 降低温度，让输出更可控
                    "max_tokens": 4000,
                    "top_p": 0.9,
                    "stream": True
                }
                
                if progress_callback:
                    progress_callback("🚀 正在初始化生成任务...")
                
                start_time = asyncio.get_event_loop().time()
                current_item = 0
                
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    ssl=True
                ) as response:
                    if response.status != 200:
                        raise Exception(f"API调用失败 (状态码: {response.status})")
                    
                    # 读取流式响应
                    full_content = ""
                    async for line in response.content:
                        if line:
                            line = line.decode('utf-8').strip()
                            if line.startswith('data: '):
                                try:
                                    data = json.loads(line[6:])
                                    if 'choices' in data and data['choices']:
                                        delta = data['choices'][0].get('delta', {})
                                        content = delta.get('content')
                                        if content:
                                            full_content += content
                                            
                                            # 更新进度信息
                                            if progress_callback:
                                                if '[' in content:
                                                    progress_callback("📊 开始生成数据结构...")
                                                elif ']' in content:
                                                    progress_callback(f"✨ 已完成全部 {num_rows} 条数据生成！")
                                                elif '{' in content:
                                                    current_item += 1
                                                    elapsed_time = asyncio.get_event_loop().time() - start_time
                                                    if current_item > 1:  # 至少有一条数据才能计算速度
                                                        avg_time_per_item = elapsed_time / current_item
                                                        remaining_items = num_rows - current_item
                                                        estimated_remaining = avg_time_per_item * remaining_items
                                                        progress_callback(
                                                            f"⏳ 正在生成第 {current_item}/{num_rows} 条数据...\n"
                                                            f"预计还需 {estimated_remaining:.1f} 秒"
                                                        )
                                                    else:
                                                        progress_callback(f"⏳ 正在生成第 {current_item}/{num_rows} 条数据...")
                                                elif '}' in content:
                                                    progress_callback(f"✅ 完成第 {current_item}/{num_rows} 条数据")
                                except json.JSONDecodeError:
                                    continue
                    
                    if progress_callback:
                        progress_callback("🔍 正在验证数据格式...")
                    
                    # 尝试从完整内容中提取JSON数据
                    try:
                        # 查找第一个 [ 和最后一个 ] 之间的内容
                        start = full_content.find('[')
                        end = full_content.rfind(']') + 1
                        if start >= 0 and end > start:
                            json_str = full_content[start:end]
                            result = json.loads(json_str)
                            
                            if len(result) != num_rows:
                                if progress_callback:
                                    progress_callback(f"⚠️ 数据数量不正确（期望{num_rows}行，实际{len(result)}行），尝试修复...")
                                
                                # 如果生成的数据太少，补充生成
                                if len(result) < num_rows:
                                    remaining_rows = num_rows - len(result)
                                    additional_prompt = (
                                        f"请继续生成{remaining_rows}行数据，"
                                        f"保持相同的格式和质量要求。"
                                        f"已有数据：{json.dumps(result, ensure_ascii=False)}"
                                    )
                                    
                                    # 递归调用生成剩余数据
                                    additional_data = await self.generate_sku_content(
                                        columns,
                                        additional_prompt,
                                        remaining_rows,
                                        progress_callback
                                    )
                                    
                                    result.extend(additional_data)
                                
                                # 如果生成的数据太多，截取需要的部分
                                elif len(result) > num_rows:
                                    result = result[:num_rows]
                                    if progress_callback:
                                        progress_callback("⚠️ 数据过多，已截取所需数量")
                            
                            if progress_callback:
                                total_time = asyncio.get_event_loop().time() - start_time
                                progress_callback(
                                    f"🎉 生成完成！\n"
                                    f"总用时：{total_time:.1f} 秒\n"
                                    f"平均速度：{num_rows/total_time:.1f} 条/秒"
                                )
                            
                            return result
                        else:
                            raise ValueError("未找到有效的JSON数组")
                    except json.JSONDecodeError as e:
                        raise Exception(f"解析JSON失败: {str(e)}\n内容: {full_content}")
                
        except Exception as e:
            if progress_callback:
                progress_callback("❌ 生成失败，请查看错误详情")
            raise Exception(f"生成SKU数据失败: {str(e)}")
    
    def _generate_mock_data(self, columns: List[str], num_rows: int, progress_callback=None) -> List[Dict[str, str]]:
        """生成模拟数据"""
        warnings.warn("使用模拟数据模式，返回测试数据。")
        mock_data = []
        
        if progress_callback:
            progress_callback("🚀 开始生成模拟数据...")
        
        for i in range(num_rows):
            if progress_callback:
                progress_callback(f"⏳ 正在生成第 {i+1}/{num_rows} 条数据...")
            
            row = {}
            for col in columns:
                if col == "价格":
                    row[col] = f"{1000 + i * 100}元"  # 添加单位
                elif col == "库存":
                    row[col] = str(100 + i * 10)  # 转换为字符串
                elif col == "身高":
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
                    row[col] = f"{col}_{i + 1}"  # 简化测试数据格式
            mock_data.append(row)
            
            if progress_callback:
                progress_callback(f"✅ 完成第 {i+1}/{num_rows} 条数据")
        
        if progress_callback:
            progress_callback("🎉 模拟数据生成完成！")
        
        return mock_data 