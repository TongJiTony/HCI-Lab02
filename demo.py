import gradio as gr
import openai
import zhipuai
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv, find_dotenv

# 加载环境变量
load_dotenv(find_dotenv())

# 获取 API Key
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
ALI_API_KEY = os.getenv("ALI_API_KEY")

# 初始化 API 客户端
ali_client = openai.OpenAI(
    api_key=ALI_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

zhipu_client = ZhipuAI(api_key=ZHIPU_API_KEY)

# 检查 API 设置是否正确
try:
    response = ali_client.chat.completions.create(
        model="qwen-turbo",  # 使用通义千问-Turbo 大模型，可以替换为 Deepseek 系列：deepseek-v3 / deepseek-r1
        messages=[{'role': 'user', 'content': "测试"}],
        max_tokens=1,
    )
    response = zhipu_client.chat.completions.create(
        model="glm-4-flash",
        messages=[{'role': 'user', 'content': "测试"}]
    )
    print("API 设置成功！！")
except Exception as e:
    print(f"API 可能有问题，请检查：{e}")

# 处理阿里云 API 响应
def get_aliyun_response(messages):
    response = ali_client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        stream=False
    )
    return response.choices[0].message.content

# 处理智谱 AI API 响应
def get_zhipuai_response(messages):
    response = zhipu_client.chat.completions.create(
        model="glm-4-flash",
        messages=messages
    )
    return response.choices[0].message.content

# 统一封装函数，实现多轮对话并展示历史记录
def chat_with_llm(user_input, chat_history_ali, chat_history_glm):
    # 添加当前用户输入到历史记录
    chat_history_ali.append({"role": "user", "content": user_input})
    chat_history_glm.append({"role": "user", "content": user_input})

    chat_history_ali.append({"role": "assistant", "content": get_aliyun_response(chat_history_ali)})
    chat_history_glm.append({"role": "assistant", "content": get_zhipuai_response(chat_history_glm)})

    return "", chat_history_ali, chat_history_glm

if __name__ == "__main__":
    # 构建 Gradio UI
    with gr.Blocks() as demo:
        gr.Markdown("# Zixun's Agent: Ask Multiple LLMs At The Same Time 多模型同时对话")
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 阿里云Qwen-Plus")
                chatbot_ali = gr.Chatbot(label="对话记录", type='messages')
            with gr.Column(scale=1):
                gr.Markdown("### 智谱GLM-4-Flush")
                chatbot_glm = gr.Chatbot(label="对话记录", type='messages')

        user_input = gr.Textbox(
            label="请输入你的问题",
            value="你好，请问你是谁？"  # 设置预设问题
        )
        chat_button = gr.Button("发送")

        chat_button.click(chat_with_llm, 
        inputs=[user_input, chatbot_ali, chatbot_glm], 
        outputs=[user_input, chatbot_ali,chatbot_glm])

    # 启动 Gradio 界面
    demo.launch()