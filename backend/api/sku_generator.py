import pandas as pd
from typing import List, Dict, Optional
from .deepseek_client import DeepSeekClient
from config import DEEPSEEK_API_KEY, DEFAULT_MODEL

class SKUGenerator:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.deepseek_client = DeepSeekClient(DEEPSEEK_API_KEY, model=model)
    
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
        progress_callback=None
    ) -> List[Dict[str, str]]:
        """生成SKU数据"""
        try:
            # 验证输入
            columns = self.validate_columns(columns)
            prompt = self.validate_prompt(prompt)
            
            if not 1 <= num_rows <= 50:
                raise ValueError("生成行数必须在1到50之间")
            
            if progress_callback:
                progress_callback("🔍 验证输入参数...")
            
            # 检查API密钥
            if not self.deepseek_client.use_mock:
                if not self.deepseek_client.api_key:
                    raise Exception("未配置API密钥")
            
            # 调用API生成数据
            result = await self.deepseek_client.generate_sku_content(
                columns,
                prompt,
                num_rows,
                progress_callback=progress_callback  # 确保正确传递回调
            )
            
            return result
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ 错误: {str(e)}")
            raise
    
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
    
    def update_api_key(self, api_key: str):
        """更新API密钥"""
        self.deepseek_client.update_api_key(api_key) 
    
    def update_model(self, model: str):
        """更新模型"""
        self.deepseek_client.update_model(model)

    def validate_existing_data(self, df: pd.DataFrame) -> None:
        """验证已有数据的格式"""
        if not isinstance(df, pd.DataFrame):
            raise ValueError("输入必须是pandas DataFrame")
        
        if df.empty:
            raise ValueError("数据不能为空")
        
        # 检查必要的列
        required_cols = set(df.columns)
        if not required_cols:
            raise ValueError("数据必须包含至少一列")
        
        # 检查数据类型
        for col in df.columns:
            if not df[col].dtype in ['object', 'string']:
                raise ValueError(f"列 '{col}' 必须是文本类型")