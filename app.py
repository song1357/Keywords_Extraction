import streamlit as st
import pandas as pd
import re

# Streamlit App
st.title("关键词提取工具")

# 使用说明
st.markdown(
    """
    ##### 使用说明
    1. **源数据要求**:
        源数据须放在源数据文件第一个sheet的A列中
    2. **字典和标签要求**:
        字典和标签须放在字典和标签文件第一个sheet的A列与B列中
    3. **使用场景**：提取源数据列中的菜品或商店名称，比如：从“46龙华麦卡淇蛋糕店”	
                    提取关键词‘麦卡淇蛋糕’或从“清香西饼屋(上马庄店)”提取关键词‘清香西饼屋’
    4. **不可缺失列名**

    """
)

# 上传第一个 Excel 文件
uploaded_file_1 = st.file_uploader("上传源数据文件", type=["xlsx"])
uploaded_file_2 = st.file_uploader("上传字典和标签文件", type=["xlsx"])

if uploaded_file_1 and uploaded_file_2:
    # 读取文件
    source_df = pd.read_excel(uploaded_file_1, sheet_name=0)
    dict_df = pd.read_excel(uploaded_file_2, sheet_name=0)

    # 自动识别列名
    source_column = source_df.columns[0]  # 假设第一个列为"源"列
    dictionary_column = dict_df.columns[0]  # 假设第一个列为"字典"
    tag_column = dict_df.columns[1]  # 假设第二个列为"标签"

    # 初始化结果 DataFrame
    result_df = source_df.copy()
    result_df.rename(columns={source_column: "源数据"}, inplace=True)
    result_df["字典"] = None
    result_df["输出结果"] = None

    # 构建正则表达式模式，按字典长度降序排列，优先匹配更长的词
    sorted_dict = sorted(dict_df[dictionary_column], key=lambda x: len(str(x)) if isinstance(x, str) else 0, reverse=True)
    pattern = "|".join(re.escape(str(x)) for x in sorted_dict if isinstance(x, str))
    compiled_pattern = re.compile(pattern)

    # 初始化进度条和状态显示
    total_rows = len(result_df)
    progress_bar = st.progress(0)
    status_text = st.empty()
    current_keyword_text = st.empty()

    # 分块处理（每次处理 500 行）
    batch_size = 500
    for start_row in range(0, total_rows, batch_size):
        end_row = min(start_row + batch_size, total_rows)
        batch = result_df.iloc[start_row:end_row]

        # 对当前批次进行匹配
        for i, source in batch["源数据"].items():
            match = compiled_pattern.search(str(source))
            if match:
                matched_keyword = match.group(0)
                tag = dict_df.loc[dict_df[dictionary_column] == matched_keyword, tag_column].values[0]
                result_df.at[i, "字典"] = matched_keyword
                result_df.at[i, "输出结果"] = tag

                # 更新当前提取的关键词
                current_keyword_text.text(f"正在提取关键词：{matched_keyword}")

        # 更新进度条
        progress = (end_row / total_rows)
        progress_bar.progress(progress)
        status_text.text(f"已处理 {end_row}/{total_rows} 行")

    # 提取完成状态
    current_keyword_text.text("已完成提取关键词")

    # 显示结果
    st.write("处理完成")
    st.dataframe(result_df)

    # 下载结果
    output_file = "关键词提取结果.xlsx"
    result_df.to_excel(output_file, index=False)
    with open(output_file, "rb") as file:
        st.download_button(
            label="下载文件",
            data=file,
            file_name=output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
