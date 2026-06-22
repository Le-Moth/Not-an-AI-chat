from flask import Flask, render_template,request
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import re
import os
from openai import OpenAI
bot = OpenAI(base_url="https://api.groq.com/openai/v1",api_key="")

engine=create_engine('sqlite:///database.db')
Base = declarative_base()
class user_text(Base):
    __tablename__ = 'chat_history_db'
    id = Column(Integer, primary_key=True, autoincrement=True)
    Text = Column(String)
    Role = Column(String)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    server_message = ""
    if request.method == 'POST':
        message = request.form.get('user')
        if message:
            User_msg = user_text(Text=message, Role="user")
            session.add(User_msg)
            session.commit()
            server_message = AI_Answer()
            server_reply=user_text(Text=server_message, Role="assistant")
            session.add(server_reply)
            session.commit()
    return render_template ('index.html', reply = server_message)
def AI_Answer():
    try:
        messages_context=[]
        messages = session.query(user_text).all()
        for i in messages:
            messages_context.append({'role':i.Role, 'content':i.Text})
        chat_completion=bot.chat.completions.create(messages=messages_context, model="qwen/qwen3-32b")
        reply=chat_completion.choices[0].message.content
        cleaned_content = re.sub(r"<think>.*?</think>\n?", "", reply, flags=re.DOTALL)
        return cleaned_content
    except Exception as e:
        print(e)
if __name__ == '__main__':
    app.run(debug=True)