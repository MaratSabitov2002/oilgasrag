import streamlit as st
from model import ChatWithAI 


st.set_page_config(page_title="Gigachat Чат", page_icon="🤖")

if "chat" not in st.session_state:
    st.session_state.model_selected = False
    st.session_state.chat = None
    st.session_state.messages = []

st.title("🤖 Чат с Gigachat")
st.write("Перед началом выберите модель. Нажмите 'Новый чат' для сброса.")

if st.button("🆕 Новый чат"):
    st.session_state.model_selected = False
    st.session_state.chat = None
    st.session_state.messages = []
    st.rerun()

if not st.session_state.model_selected:
    model = st.selectbox("Выберите модель:", ["gigachat-lite", "gigachat-pro", "gigachat-max"])
    if st.button("🚀 Начать чат"):
        st.session_state.chat = ChatWithAI(provider=model)
        st.session_state.model_selected = True
        st.session_state.messages = []
        st.success(f"Чат с моделью **{model}** создан.")
        st.rerun()
    st.stop()

user_input = st.chat_input("Введите сообщение")

if user_input:
    st.session_state.messages.append(("Вы", user_input))
    st.session_state.chat.get_relevant_context(user_input)

    with st.spinner("ИИ печатает..."):
        response = st.session_state.chat.generate_response(user_input)

    st.session_state.messages.append(("ИИ", response))

for sender, message in st.session_state.messages:
    with st.chat_message("user" if sender == "Вы" else "assistant"):
        st.markdown(message)

