import streamlit as st
import pandas as pd
import re

# Streamlit App
st.title("关键词提取工具")

# 上传第一个 Excel 文件
uploaded_file_1 = st.file_uploader("上传包含'源'列的 Excel 文件", type=["xlsx"])
uploaded_file_2 = st.file_uploader("上传包含'字典'和'标签'列的 Excel 文件", type=["xlsx"])

if uploaded_file_1 and uploaded_file_2:
    # 读取文件
    source_df = pd.read_excel(uploaded_file_1, sheet_name=0)
    dict_df = pd.read_excel(uploaded_file_2, sheet_name=0)

    # 确保必要的列存在
    if "源" in source_df.columns and "字典" in dict_df.columns and "标签" in dict_df.columns:
        # 初始化结果 DataFrame
        result_df = source_df.copy()
        result_df["字典"] = None
        result_df["输出结果"] = None

        # 构建正则表达式模式
        pattern = "|".join(re.escape(str(x)) for x in dict_df["字典"] if isinstance(x, str))
        compiled_pattern = re.compile(pattern)

        # 初始化进度条
        total_rows = len(result_df)
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 分块处理（每次处理 500 行）
        batch_size = 500
        for start_row in range(0, total_rows, batch_size):
            end_row = min(start_row + batch_size, total_rows)
            batch = result_df.iloc[start_row:end_row]

            # 对当前批次进行匹配
            for i, source in batch["源"].items():
                match = compiled_pattern.search(str(source))
                if match:
                    matched_keyword = match.group(0)
                    tag = dict_df.loc[dict_df["字典"] == matched_keyword, "标签"].values[0]
                    result_df.at[i, "字典"] = matched_keyword
                    result_df.at[i, "输出结果"] = tag

            # 更新进度条
            progress = (end_row / total_rows)
            progress_bar.progress(progress)
            status_text.text(f"已处理 {end_row}/{total_rows} 行")

        # 显示结果
        st.write("处理完成！")
        st.dataframe(result_df)

        # 下载结果
        output_file = "关键词提取结果.xlsx"
        result_df.to_excel(output_file, index=False)
        with open(output_file, "rb") as file:
            st.download_button(
                label="下载结果文件",
                data=file,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    else:
        st.error("请确保文件包含必要的列：'源' 和 '字典/标签'")
