import streamlit as st
from openai import OpenAI
import json

def create_openai_client(api_key, api_base):
    return OpenAI(api_key=api_key, base_url=api_base)

def main():
    st.title("DeepSeek API 聊天界面")
    
    # 侧边栏配置
    with st.sidebar:
        st.header("配置参数")
        api_key = st.text_input("API Key", type="password")
        api_base = st.text_input("API Base URL", 
                                value="https://api.deepseek.com",
                                help="DeepSeek API的基础URL")
        
        model = st.selectbox("选择模型", 
                           ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"])
        
        st.subheader("模型参数")
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 
                              help="控制输出的随机性")
        top_p = st.slider("Top P", 0.0, 1.0, 0.9, 
                         help="核采样阈值")
        max_tokens = st.number_input("最大输出长度", 1, 4096, 1024)

    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "reasoning_content" in message:
                with st.expander("推理过程"):
                    st.markdown(message["reasoning_content"])

    # 用户输入
    if prompt := st.chat_input("输入您的问题"):
        if not api_key:
            st.error("请先输入 API Key")
            return

        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 调用API获取响应
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    client = create_openai_client(api_key, api_base)
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": m["role"], "content": m["content"]} 
                                for m in st.session_state.messages],
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens
                    )
                    
                    assistant_response = response.choices[0].message.content
                    st.markdown(assistant_response)
                    
                    # 如果是 deepseek-reasoner 模型，显示推理过程
                    assistant_message = {
                        "role": "assistant",
                        "content": assistant_response
                    }
                    
                    if model == "deepseek-reasoner":
                        reasoning_content = response.choices[0].message.reasoning_content
                        assistant_message["reasoning_content"] = reasoning_content
                        with st.expander("推理过程"):
                            st.markdown(reasoning_content)
                    
                    st.session_state.messages.append(assistant_message)
                    
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()