

import streamlit as st
import openai
from htmlTemplates import css, bot_template, user_template


openai.api_key = "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"
st.write(css,unsafe_allow_html=True)

messages = [
    {"role": "system", "content": "You are a helpful and kind AI Assistant."},
]

def chatbot(input):
    if input:
        messages.append({"role": "user", "content": input})
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        reply = chat.choices[0].message.content

        #st.write(reply)
        messages.append({"role": "assistant", "content": reply})
       # session_state = SessionState.get(text_input='')
        user_input = ""
        st.write(bot_template.replace("{{MSG}}",reply), unsafe_allow_html=True)

        return reply

# st.title("Chatbot")

#form = st.form(key='chat_form')

user_input = st.text_input("Hello, I am Adaza, how can I help you today?")

#submit_button = form.form_submit_button("Send")



if user_input:
    with st.spinner("Processing..."):
        st.write(user_template.replace("{{MSG}}",user_input), unsafe_allow_html=True)
        response = chatbot(user_input)
        #st.write(response)
        #st.text_area("Adaza", value=response, height=200)




