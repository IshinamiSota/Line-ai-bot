from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, TextSendMessage
import openai
import base64

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = "fpYeoFSVtnMpt0DqKQLF3VN6ga44FN3Ayy9OUdct/alvFu/GpIwIw1nNv7kimN3tS9qgYo5dg9bz0lj0jMAXt7jZ+Dvlg/KHBf8o2L9lX4Oo9cwX7BjTGny+93lfde/A4kr6HBBZeIfEt6Boe3pS1gdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "da4a94eb3f4cb9c6521bba9a761480fb"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

import os

openai.api_key =os.getenv("OPENAI_API_KEY")

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    image_bytes = message_content.content
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは外壁診断と見積もりAIです。"},
            {"role": "user", "content": [
                {"type": "input_image", "image": image_base64},
                {"type": "text", "text": "この外壁の状態を診断し、劣化レベルと概算見積もりを出してください。"}
            ]}
        ]
    )

    ai_reply = response["choices"][0]["message"]["content"]

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ai_reply)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
