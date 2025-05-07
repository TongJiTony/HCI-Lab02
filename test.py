import gradio as gr
import requests
import os
import json
from typing import List, Dict, Tuple
import openai
import gradio as gr
import zhipuai
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import gradio as gr
import os
import openai
import zhipuai

# 初始化 API Key
zhipuai.api_key = os.getenv("ZHIPU_API_KEY")
ALI_API_KEY = os.getenv("ALI_API_KEY")

# 初始化 OpenAI 客户端，使用阿里云 DashScope API
ali_client = openai.OpenAI(
    api_key=ALI_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 定义获取阿里云回复的方法
def get_aliyun_response(messages):
    """调用阿里云 DashScope API"""
    response = ali_client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        stream=False  # 同步请求
    )
    return response.choices[0].message.content

# 定义获取智谱 AI 回复的方法
def get_zhipuai_response(messages):
    """调用智谱 AI API"""
    zhipu_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
    response = zhipuai.model_api.invoke(
        model="glm-4",
        messages=zhipu_messages,
        temperature=0.7
    )
    return response["data"]["choices"][0]["content"]

# 统一封装函数，根据用户选择的模型调用不同的 API
def chat_with_llm(user_input, model_choice):
    messages = [{"role": "user", "content": user_input}]
    
    if model_choice == "阿里云通义千问":
        return get_aliyun_response(messages)
    elif model_choice == "智谱 GLM":
        return get_zhipuai_response(messages)
    else:
        return "请选择一个有效的模型！"

# 构建 Gradio 可视化界面
with gr.Blocks() as demo:
    gr.Markdown("# LLM 对话界面")
    
    with gr.Row():
        user_input = gr.Textbox(label="输入你的问题")
        model_choice = gr.Radio(["阿里云通义千问", "智谱 GLM"], label="选择大模型")

    chat_button = gr.Button("发送")
    output = gr.Textbox(label="LLM 回复")

    chat_button.click(chat_with_llm, inputs=[user_input, model_choice], outputs=output)

# 启动 Gradio 页面
demo.launch()