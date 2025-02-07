import streamlit as st
import pandas as pd
import asyncio
import sys
from pathlib import Path
from io import BytesIO

# 添加项目根目录到Python路径
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from backend.api.sku_generator import SKUGenerator
from config import SUPPORTED_MODELS, DEFAULT_MODEL

def init_session_state():
    if 'sku_columns' not in st.session_state:
        st.session_state.sku_columns = []
    if 'sku_data' not in st.session_state:
        st.session_state.sku_data = None

async def generate_sku_data(generator, columns, prompt, num_rows, progress_callback=None):
    """异步生成SKU数据"""
    return await generator.generate_sku_data(
        columns, 
        prompt, 
        num_rows,
        progress_callback=progress_callback
    )

def show_error_details(error: Exception):
    """显示错误详情"""
    with st.expander("查看错误详情"):
        st.error(str(error))

def show_help():
    """显示帮助信息"""
    with st.sidebar.expander("使用帮助 ❓"):
        st.markdown("""
        ### 如何使用
        1. 在左侧输入SKU属性（每行一个）
        2. 点击"创建SKU模板"
        3. 输入产品描述或关键词
        4. 设置要生成的行数
        5. 点击"生成SKU数据"
        
        ### 注意事项
        - SKU属性不能重复
        - 每个属性必须有值
        - 生成行数限制在1-50行之间
        """)

def show_api_settings():
    """显示API设置"""
    with st.sidebar.expander("API设置 ⚙️", expanded=False):
        # 初始化会话状态
        if 'api_key' not in st.session_state:
            st.session_state.api_key = None
            st.session_state.use_mock = True
            st.session_state.model = DEFAULT_MODEL
        
        # 模型选择
        model = st.selectbox(
            "选择模型",
            options=list(SUPPORTED_MODELS.keys()),
            index=list(SUPPORTED_MODELS.keys()).index(st.session_state.model),
            format_func=lambda x: f"{x} - {SUPPORTED_MODELS[x]['description']}",
            help="选择要使用的模型"
        )
        
        # API密钥输入
        api_key = st.text_input(
            "DeepSeek API密钥",
            type="password",
            value=st.session_state.api_key if st.session_state.api_key else "",
            help="在 https://platform.deepseek.com/ 获取API密钥"
        )
        
        # 模拟模式切换
        use_mock = st.checkbox(
            "使用模拟数据",
            value=st.session_state.use_mock,
            help="开启后将返回测试数据，无需API密钥"
        )
        
        if st.button("保存设置", use_container_width=True):
            if api_key and not use_mock:
                if not api_key.startswith('sk-'):
                    st.error("❌ API密钥格式不正确，应以'sk-'开头")
                    return
            st.session_state.api_key = api_key
            st.session_state.use_mock = use_mock
            st.session_state.model = model
            st.success("✅ 设置已保存")
            
        # 显示当前状态
        st.markdown("---")
        st.markdown("**当前状态**")
        st.markdown(f"🤖 模型：**{st.session_state.model}**")
        if use_mock:
            st.info("🔄 使用模拟数据模式")
        elif api_key:
            st.success("🔑 已配置API密钥")
        else:
            st.warning("⚠️ 未配置API密钥")

def show_progress(total_rows: int):
    """显示生成进度"""
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    def update_progress(message: str):
        progress_text.text(message)
    
    return update_progress

def main():
    st.set_page_config(
        page_title="DataSprite - 智能SKU生成器",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 显示帮助信息
    show_help()
    
    # 显示API设置
    show_api_settings()
    
    st.title("DataSprite 数据精灵 🧚‍♂️")
    init_session_state()
    
    # 侧边栏：输入SKU属性
    with st.sidebar:
        st.header("SKU属性设置")
        columns_input = st.text_area(
            "请输入SKU属性（每行一个）",
            placeholder="例如：\n商品名称\n规格\n颜色\n材质",
            help="每行输入一个属性名称，属性名称不能重复"
        )
        
        if st.button("创建SKU模板", type="primary"):
            try:
                if not columns_input:
                    raise ValueError("请输入SKU属性")
                
                generator = SKUGenerator()
                columns = generator.validate_columns(columns_input.split('\n'))
                
                st.session_state.sku_columns = columns
                st.session_state.sku_data = pd.DataFrame(columns=columns)
                st.success("✅ SKU模板创建成功！")
            except Exception as e:
                st.error("❌ 创建模板失败")
                show_error_details(e)
    
    # 主界面：生成SKU内容
    if st.session_state.sku_columns:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("SKU生成设置")
            prompt = st.text_area(
                "请输入产品描述或关键词",
                placeholder="例如：高科技智能手表，支持心率监测、运动追踪等功能...",
                help="详细的描述可以帮助生成更准确的数据"
            )
            
            num_rows = st.number_input(
                "生成行数",
                min_value=1,
                max_value=50,
                value=5,
                help="一次最多生成50行数据"
            )
            
            col1_1, col1_2, col1_3 = st.columns(3)
            with col1_1:
                generate_button = st.button(
                    "生成SKU数据",
                    type="primary",
                    use_container_width=True
                )
            
            if generate_button:
                try:
                    if not prompt:
                        raise ValueError("请输入产品描述或关键词")
                    
                    with st.spinner("准备生成数据..."):
                        generator = SKUGenerator(model=st.session_state.model)
                        
                        # 使用保存的设置
                        if st.session_state.api_key and not st.session_state.use_mock:
                            generator.update_api_key(st.session_state.api_key)
                        generator.deepseek_client.use_mock = st.session_state.use_mock
                        
                        # 如果不是模拟模式且没有API密钥，显示错误
                        if not st.session_state.use_mock and not st.session_state.api_key:
                            raise ValueError("请先配置DeepSeek API密钥或启用模拟数据模式")
                        
                        progress_callback = show_progress(num_rows)
                        
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            # 一次性生成所有数据
                            data = loop.run_until_complete(
                                generate_sku_data(
                                    generator,
                                    st.session_state.sku_columns,
                                    prompt,
                                    num_rows,
                                    progress_callback=progress_callback
                                )
                            )
                            
                            st.session_state.sku_data = pd.DataFrame(data)
                            st.success("✅ SKU数据生成成功！")
                        finally:
                            loop.close()
                except Exception as e:
                    st.error("❌ 生成失败")
                    show_error_details(e)
        
        with col2:
            st.subheader("数据预览")
            if st.session_state.sku_data is not None:
                # 添加编辑功能
                edited_df = st.data_editor(
                    st.session_state.sku_data,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="dynamic"
                )
                
                # 更新编辑后的数据
                st.session_state.sku_data = edited_df
                
                # 导出功能
                if not edited_df.empty:
                    col2_1, col2_2 = st.columns(2)
                    with col2_1:
                        csv = edited_df.to_csv(index=False)
                        st.download_button(
                            "下载CSV文件",
                            csv,
                            "sku_data.csv",
                            "text/csv",
                            key='download-csv',
                            use_container_width=True
                        )
                    with col2_2:
                        excel_buffer = BytesIO()
                        edited_df.to_excel(excel_buffer, index=False)
                        excel_data = excel_buffer.getvalue()
                        st.download_button(
                            "下载Excel文件",
                            excel_data,
                            "sku_data.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key='download-excel',
                            use_container_width=True
                        )

if __name__ == "__main__":
    main() 