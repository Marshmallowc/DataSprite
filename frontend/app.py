import streamlit as st
import pandas as pd
import asyncio
import sys
from pathlib import Path
from io import BytesIO
import json

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
    with st.sidebar.expander("API设置 ⚙️"):
        # 选择模型
        model = st.selectbox(
            "选择模型",
            options=list(SUPPORTED_MODELS.keys()),
            index=list(SUPPORTED_MODELS.keys()).index(DEFAULT_MODEL),
            format_func=lambda x: f"{x} - {SUPPORTED_MODELS[x]['description']}"
        )
        st.session_state.model = model
        
        # API密钥设置
        api_key = st.text_input(
            "DeepSeek API密钥",
            type="password",
            help="在 https://platform.deepseek.com/ 获取"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            if st.button("更新API密钥"):
                try:
                    generator = SKUGenerator(model=model)
                    generator.update_api_key(api_key)
                    st.success("✅ API密钥更新成功！")
                except Exception as e:
                    st.error("❌ API密钥更新失败")
                    show_error_details(e)

def show_progress(total_rows: int):
    """显示生成进度"""
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    def update_progress(message: str):
        progress_text.text(message)
    
    return update_progress

def add_file_uploader():
    """添加文件上传功能"""
    uploaded_file = st.file_uploader(
        "上传已有SKU文件", 
        type=['csv', 'xlsx'],
        help="支持CSV和Excel文件"
    )
    
    if uploaded_file is not None:
        try:
            # 根据文件类型读取
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # 更新session state
            st.session_state.sku_columns = list(df.columns)
            st.session_state.sku_data = df
            
            return df
        except Exception as e:
            st.error(f"读取文件失败: {str(e)}")
            return None
    return None

async def continue_generation(df: pd.DataFrame, num_new_rows: int):
    """从已有数据继续生成"""
    if df is None or df.empty:
        st.error("没有可用的数据")
        return None
    
    generator = SKUGenerator(model=st.session_state.model)
    # 如果有API密钥，使用API模式
    if 'api_key' in st.session_state and st.session_state.api_key:
        generator.update_api_key(st.session_state.api_key)
        generator.deepseek_client.use_mock = False
    else:
        generator.deepseek_client.use_mock = True
    
    # 获取现有数据的特征
    columns = list(df.columns)
    last_row = df.iloc[-1].to_dict()
    
    # 构建更好的prompt
    prompt = (
        f"请生成新的SKU数据，参考以下已有数据的格式和风格：\n\n"
        f"已有数据最后一行：\n"
        + "\n".join([f"- {col}: {val}" for col, val in last_row.items()])
        + "\n\n要求：\n"
        "1. 生成全新的数据，不要复制已有数据\n"
        "2. 保持数据格式一致性\n"
        "3. 数据要合理且多样化\n"
        "4. 避免与最后一行数据重复\n"
        f"5. 确保生成{num_new_rows}条不同的数据"
    )
    
    # 创建一个固定的进度显示区域
    progress_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    def progress_callback(message: str):
        # 更新进度显示
        if "正在生成第" in message:
            try:
                current = int(message.split('/')[0].split('第')[-1])
                progress_bar.progress(current / num_new_rows)
            except:
                pass
        progress_placeholder.text(message)
    
    try:
        with st.spinner("正在生成新数据..."):
            new_data = await generator.generate_sku_data(
                columns=columns,
                prompt=prompt,
                num_rows=num_new_rows,
                progress_callback=progress_callback
            )
            
            if new_data:
                progress_placeholder.empty()  # 清除进度显示
                progress_bar.empty()         # 清除进度条
                # 转换为DataFrame并合并
                new_df = pd.DataFrame(new_data)
                result_df = pd.concat([df, new_df], ignore_index=True)
                st.success(f"成功生成{num_new_rows}条新数据！")
                return result_df
            
            st.error("未能生成新数据")
            return None
            
    except Exception as e:
        st.error(f"生成失败: {str(e)}")
        return None

def show_file_upload_page():
    """显示文件上传页面"""
    # 显示帮助信息
    show_help()
    
    # 显示API设置（与创建新文件页面共用同一个设置面板）
    show_api_settings()
    
    # 文件上传部分
    df = add_file_uploader()
    if df is not None:
        st.write("当前数据预览：")
        # 直接显示数据框
        st.dataframe(df)
        
        # 继续生成选项
        with st.form("continue_generation"):
            num_new_rows = st.number_input(
                "要生成的新数据行数",
                min_value=1,
                max_value=50,
                value=5
            )
            
            if st.form_submit_button("继续生成"):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    updated_df = loop.run_until_complete(continue_generation(df, num_new_rows))
                    if updated_df is not None:
                        st.session_state.sku_data = updated_df
                        st.dataframe(updated_df)  # 直接显示更新后的数据
                finally:
                    loop.close()

def create_new_file():
    """创建新文件的功能"""
    # 显示帮助信息
    show_help()
    
    # 显示API设置
    show_api_settings()
    
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
    
    # 显示数据编辑器
    show_data_editor()

def show_data_editor():
    """显示数据编辑器和导出功能"""
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
            
            if st.button("生成SKU数据", type="primary"):
                # 使用事件循环运行异步函数
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(generate_data(prompt, num_rows))
                    # 刷新数据预览
                    st.rerun()
                finally:
                    loop.close()
        
        with col2:
            st.subheader("数据预览")
            if st.session_state.sku_data is not None:
                show_data_preview()

def show_data_preview():
    """显示数据预览和导出功能"""
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
        col1, col2 = st.columns(2)
        with col1:
            csv = edited_df.to_csv(index=False)
            st.download_button(
                "下载CSV文件",
                csv,
                "sku_data.csv",
                "text/csv",
                key='download-csv',
                use_container_width=True
            )
        with col2:
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

async def generate_data(prompt: str, num_rows: int):
    """生成SKU数据"""
    if not st.session_state.sku_columns:
        st.error("请先创建SKU模板")
        return
    
    if not prompt:
        st.error("请输入产品描述或关键词")
        return
    
    try:
        generator = SKUGenerator(model=st.session_state.model)
        
        # 设置API密钥和模式
        if 'api_key' in st.session_state and st.session_state.api_key:
            generator.update_api_key(st.session_state.api_key)
            generator.deepseek_client.use_mock = False  # 使用API模式
        else:
            generator.deepseek_client.use_mock = True  # 使用模拟模式
        
        # 显示进度
        progress_callback = show_progress(num_rows)
        
        # 生成数据
        with st.spinner("正在生成数据..."):
            result = await generator.generate_sku_data(
                st.session_state.sku_columns,
                prompt,
                num_rows,
                progress_callback=progress_callback
            )
            
            # 更新数据
            new_df = pd.DataFrame(result)
            if st.session_state.sku_data is None:
                st.session_state.sku_data = new_df
            else:
                st.session_state.sku_data = pd.concat(
                    [st.session_state.sku_data, new_df],
                    ignore_index=True
                )
            
            st.success(f"✨ 成功生成{num_rows}条数据！")
            
    except Exception as e:
        st.error("❌ 生成失败")
        show_error_details(e)

def main():
    st.set_page_config(
        page_title="DataSprite - 智能SKU生成器",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧚‍♂️ DataSprite SKU生成器")
    
    # 初始化session state
    init_session_state()
    
    # 侧边栏：选择操作模式
    mode = st.sidebar.radio(
        "选择操作模式",
        ["创建新文件", "打开已有文件"]
    )
    
    if mode == "创建新文件":
        create_new_file()
    else:
        show_file_upload_page()

if __name__ == "__main__":
    main() 