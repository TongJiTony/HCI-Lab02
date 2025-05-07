import os
import json
from typing import List, Dict, Tuple
import openai
import gradio as gr
import zhipuai
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# 初始化客户端
zhipuai.api_key = os.getenv("ZHIPU_API_KEY")

OPENAI_API_KEY = os.getenv('ALI_API_KEY')

# 初始化 OpenAI 客户端，使用阿里云 DashScope API
client = openai.OpenAI(
    api_key = OPENAI_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 阿里云的 API 地址
)

# 检查 API 设置是否正确
try:
    response = client.chat.completions.create(
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
    response = zhipuai.model_api.invoke(
        model="glm-4",
        messages=zhipu_messages,
        temperature=0.7
    )
    return response["data"]["choices"][0]["content"]

def respond(user_input, chat_history):
    # 初始化系统消息
    messages = [{"role": "system", "content": "你是专业的手机推荐助手"}]
    
    # 添加历史对话
    for user_msg, bot_msg in chat_history:
        messages.extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": bot_msg}
        ])
    
    # 添加新输入
    messages.append({"role": "user", "content": user_input})
    
    # 获取双模型响应
    ali_response = get_aliyun_response(messages)
    zhipu_response = get_zhipuai_response(messages)
    
    # 合并响应
    full_response = f"**阿里云Qwen**\n{ali_response}\n\n**智谱GLM**\n{zhipu_response}"
    chat_history.append((user_input, full_response))
    return "", chat_history  # 清空输入框

PROMPT_FOR_SUMMARIZATION = "请将以下文章概括成几句话。"

def reset():
    """
    清空对话记录

    返回:
        List: 空的对话记录列表
    """
    return []

def interact_summarization(prompt, article, temp=1.0):
    """
    调用模型生成摘要。

    参数:
        prompt (str): 用于摘要的提示词
        article (str): 需要摘要的文章内容
        temp (float): 模型温度，控制输出创造性（默认 1.0）

    返回:
        List[Tuple[str, str]]: 对话记录，包含输入文本与模型输出
    """
    # 合成请求文本
    input_text = f"{prompt}\n{article}"
    
    response = client.chat.completions.create(
        model="qwen-turbo",  # 使用通义千问-Turbo大模型
        messages=[{'role': 'user', 'content': input_text}],
        temperature=temp,
    )
    return [(input_text, response.choices[0].message.content)]

def export_summarization(chatbot, article):
    """
    导出摘要任务的对话记录和文章内容到 JSON 文件。

    参数:
        chatbot (List[Tuple[str, str]]): 模型对话记录
        article (str): 文章内容
    """
    target = {"chatbot": chatbot, "article": article}
    with open("files/part1.json", "w", encoding="utf-8") as file:
        json.dump(target, file, ensure_ascii=False, indent=4)

# 构建 Gradio UI 界面
with gr.Blocks() as demo:
    gr.Markdown("# 第1部分：摘要\n填写任何你喜欢的文章，让聊天机器人为你总结！")
    chatbot = gr.Chatbot(type='messages')
    prompt_textbox = gr.Textbox(label="提示词", value=PROMPT_FOR_SUMMARIZATION, visible=False)
    article_textbox = gr.Textbox(label="文章", interactive=True, value="填充")
    
    with gr.Column():
        gr.Markdown("# 温度调节\n温度用于控制聊天机器人的输出，温度越高，响应越具创造性。")
        temperature_slider = gr.Slider(0.0, 2.0, 1.0, step=0.1, label="温度")
    
    with gr.Row():
        send_button = gr.Button(value="发送")
        reset_button = gr.Button(value="重置")
    
    with gr.Column():
        gr.Markdown("# 保存结果\n当你对结果满意后，点击导出按钮保存结果。")
        export_button = gr.Button(value="导出")
    
    # 绑定按钮与回调函数
    send_button.click(interact_summarization,
                      inputs=[prompt_textbox, article_textbox, temperature_slider],
                      outputs=[chatbot])
    reset_button.click(reset, outputs=[chatbot])
    export_button.click(export_summarization, inputs=[chatbot, article_textbox])


if __name__ == "__main__":
    print(os.getenv("ALI_API_KEY"))
    demo.launch(debug=True)