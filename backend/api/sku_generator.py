import pandas as pd
from typing import List, Dict, Optional
from .deepseek_client import DeepSeekClient
from config import DEEPSEEK_API_KEY

class SKUGenerator:
    def __init__(self):
        self.deepseek_client = DeepSeekClient(DEEPSEEK_API_KEY)
    
    def validate_columns(self, columns: List[str]) -> List[str]:
        """验证并清理列名"""
        if not columns:
            raise ValueError("列名不能为空")
        
        # 清理列名
        cleaned_columns = [col.strip() for col in columns if col.strip()]
        if not cleaned_columns:
            raise ValueError("清理后的列名不能为空")
        
        # 检查重复列名
        if len(cleaned_columns) != len(set(cleaned_columns)):
            raise ValueError("列名不能重复")
            
        return cleaned_columns
    
    def validate_prompt(self, prompt: str) -> str:
        """验证并清理提示词"""
        if not prompt or not prompt.strip():
            raise ValueError("提示词不能为空")
        return prompt.strip()
    
    async def create_sku_template(self, columns: List[str]) -> pd.DataFrame:
        """创建SKU模板"""
        return pd.DataFrame(columns=columns)
    
    async def generate_sku_data(
        self, 
        columns: List[str], 
        prompt: str, 
        num_rows: int,
        retries: int = 3
    ) -> List[Dict[str, str]]:
        """生成SKU数据，支持重试"""
        # 验证输入
        columns = self.validate_columns(columns)
        prompt = self.validate_prompt(prompt)
        
        if not 1 <= num_rows <= 50:
            raise ValueError("生成行数必须在1到50之间")
        
        # 尝试生成数据，支持重试
        last_error = None
        for attempt in range(retries):
            try:
                data = await self.deepseek_client.generate_sku_content(
                    columns,
                    prompt,
                    num_rows
                )
                # 验证生成的数据
                self.validate_generated_data(data, columns)
                return data
            except Exception as e:
                last_error = e
                if attempt < retries - 1:  # 如果还有重试机会
                    continue
                raise Exception(f"生成SKU数据失败（已重试{retries}次）: {str(last_error)}")
    
    def validate_generated_data(
        self, 
        data: List[Dict[str, str]], 
        expected_columns: List[str]
    ) -> None:
        """验证生成的数据是否符合要求"""
        if not isinstance(data, list):
            raise ValueError("生成的数据必须是列表")
        
        for row in data:
            if not isinstance(row, dict):
                raise ValueError("生成的每行数据必须是字典")
            
            # 检查列名是否完整
            missing_cols = set(expected_columns) - set(row.keys())
            if missing_cols:
                raise ValueError(f"生成的数据缺少以下列：{missing_cols}")
            
            # 检查值是否为空
            empty_cols = [col for col, val in row.items() if not str(val).strip()]
            if empty_cols:
                raise ValueError(f"以下列的值不能为空：{empty_cols}") 