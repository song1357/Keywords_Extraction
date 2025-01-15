import streamlit as st
import pandas as pd

# Streamlit App
st.title("关键词提取工具")

# 上传第一个 Excel 文件
uploaded_file_1 = st.file_uploader("上传包含'源'列的 Excel 文件", type=["xlsx"])
# 上传第二个 Excel 文件
uploaded_file_2 = st.file_uploader("上传包含'字典'和'标签'列的 Excel 文件", type=["xlsx"])

if uploaded_file_1 and uploaded_file_2:

    # 读取文件
    source_df = pd.read_excel(uploaded_file_1, sheet_name=0)
    dict_df = pd.read_excel(uploaded_file_2, sheet_name=0)

    # 确保必要的列存在
    if "源" in source_df.columns and "字典" in dict_df.columns and "标签" in dict_df.columns:
        # 创建一个结果 DataFrame，与 source_df 相同结构，添加空的“字典”和“输出结果”列
        result_df = source_df.copy()
        result_df["字典"] = None
        result_df["输出结果"] = None

        # 遍历每个源数据，进行匹配
        for i, source in result_df["源"].items():
            for _, row in dict_df.iterrows():
                dictionary, tag = row["字典"], row["标签"]
                if isinstance(dictionary, str) and dictionary in str(source):
                    result_df.at[i, "字典"] = dictionary
                    result_df.at[i, "输出结果"] = tag
                    break

        # 显示结果
        st.write("处理结果：")
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
