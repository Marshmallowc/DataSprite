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

def init_session_state():
    if 'sku_columns' not in st.session_state:
        st.session_state.sku_columns = []
    if 'sku_data' not in st.session_state:
        st.session_state.sku_data = None

async def generate_sku_data(generator, columns, prompt, num_rows):
    """异步生成SKU数据"""
    return await generator.generate_sku_data(columns, prompt, num_rows)

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

def main():
    st.set_page_config(
        page_title="智能SKU生成器",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 显示帮助信息
    show_help()
    
    st.title("智能SKU生成器 🎯")
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
                    
                    with st.spinner("正在生成SKU数据..."):
                        generator = SKUGenerator()
                        generator.deepseek_client.use_mock = True
                        
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            data = loop.run_until_complete(
                                generate_sku_data(
                                    generator,
                                    st.session_state.sku_columns,
                                    prompt,
                                    num_rows
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