import gradio as gr
import openai
import zhipuai
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
ALI_API_KEY = os.getenv("ALI_API_KEY")

# 初始化 API 客户端
ali_client = openai.OpenAI(
    api_key=ALI_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 阿里云的 API 地址
)

zhipu_client = ZhipuAI(api_key=ZHIPU_API_KEY)

# 存储对话历史
chat_history = []

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
        stream=False  # 同步请求
    )
    return response.choices[0].message.content

# 处理智谱 AI API 响应
def get_zhipuai_response(messages):
    response = zhipu_client.chat.completions.create(
        model="glm-4-flash",
        messages=messages
    )
    return response.choices[0].message.content

# 统一封装函数，实现多轮对话
def chat_with_llm(user_input, model_choice):
    global chat_history

    # 添加当前用户输入到历史记录
    chat_history.append({"role": "user", "content": user_input})

    # 选择调用对应的模型
    if model_choice == "Qwen":
        response_content = get_aliyun_response(chat_history)
    elif model_choice == "ZHIPU":
        response_content = get_zhipuai_response(chat_history)
    else:
        return "请选择一个有效的模型！"

    # 记录 AI 的回复到历史记录
    chat_history.append({"role": "assistant", "content": response_content})

    return response_content

# 构建 Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# LLM 多轮对话界面")
    
    with gr.Row():
        user_input = gr.Textbox(label="输入你的问题")
        model_choice = gr.Radio(["Qwen", "ZHIPU"], label="选择大模型")

    chat_button = gr.Button("发送")
    output = gr.Textbox(label="LLM 回复")

    chat_button.click(chat_with_llm, inputs=[user_input, model_choice], outputs=output)

# 启动 Gradio 界面
demo.launch()