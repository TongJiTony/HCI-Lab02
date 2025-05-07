import gradio as gr
import openai
import zhipuai
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# 初始化客户端
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
ALI_API_KEY = os.getenv('ALI_API_KEY')

# 初始化 OpenAI 客户端，使用阿里云 DashScope API
ali_client = openai.OpenAI(
    api_key = ALI_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 阿里云的 API 地址
)

zhipu_client = ZhipuAI(api_key=ZHIPU_API_KEY)

# 检查 API 设置是否正确
try:
    response = ali_client.chat.completions.create(
        model="qwen-turbo",  # 使用通义千问-Turbo 大模型，可以替换为 Deepseek 系列：deepseek-v3 / deepseek-r1
        messages=[{'role': 'user', 'content': "测试"}],
        max_tokens=1,
    )
    print("API 设置成功！！")
except Exception as e:
    print(f"API 可能有问题，请检查：{e}")

def get_aliyun_response(messages):
    """阿里云同步响应"""
    response = ali_client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        stream=False  # 同步请求
    )
    return response.choices[0].message.content


def get_zhipuai_response(messages):
    """智谱AI同步响应"""
    zhipu_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
    response = client.chat.completions.create(
    model="glm-4-plus",  # 请填写您要调用的模型名称
    messages=[
        {"role": "user", "content": "作为一名营销专家，请为我的产品创作一个吸引人的口号"},
        {"role": "assistant", "content": "当然，要创作一个吸引人的口号，请告诉我一些关于您产品的信息"},
        {"role": "user", "content": "智谱AI开放平台"},
        {"role": "assistant", "content": "点燃未来，智谱AI绘制无限，让创新触手可及！"},
        {"role": "user", "content": "创作一个更精准且吸引人的口号"}
    ],
)
    return response["data"]["choices"][0]["content"]


# Function to call the LLM API
def chat_with_llm(user_input, model_choice):
    if model_choice == "Qwen":
        response = get_aliyun_response(user_input)
    else:
        response = get_zhipuai_response(user_input)

    return response

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# LLM Chat Interface")
    
    with gr.Row():
        user_input = gr.Textbox(label="Enter your message")
        model_choice = gr.Radio(["Qwen", "ZHIPU"], label="Choose LLM Model")
    
    chat_button = gr.Button("Send")
    output = gr.Textbox(label="LLM Response")

    chat_button.click(chat_with_llm, inputs=[user_input, model_choice], outputs=output)

# Launch the interface
demo.launch()