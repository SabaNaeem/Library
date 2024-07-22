import streamlit as st
import requests


def default_page():
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
            <h2>I will answer your questions</h2>
            <p>Get started with blabla</p>
        </div>
        """, unsafe_allow_html=True)
    st.write("")
    st.write("")
    st.write("")
    def icon_with_text():
        col4, col5, col6 = st.columns([1, 2, 1])
        with col4:
            st.write("")
        with col5:
            st.markdown(
                """
                <div style="text-align: center;">
                    <img src="icons8-guide-48.png" style='width:30px;'/>
                    <p style="margin: 0;">Guides</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col6:
            st.write("")

    col1, col2, col3 = st.columns(3)
    with col1:
        icon_with_text()
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)
    with col2:
        icon_with_text()
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)
    with col3:
        icon_with_text()
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)

prompt = st.chat_input("Type your text here and magic will happen")
def new_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['text'])

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({'role': 'user', 'text': prompt})
        params = {
            'text': prompt
        }
        if not "messages" in st.session_state:
            session = create_session(params)
            print(session)

        headers = {
            'Authorization': f'Bearer {st.session_state["access_token"]}',
            'Content-Type': 'application/json'
        }
        api_url = f"http://localhost:3000/{prompt}"

        response = requests.post(api_url, json=params, headers=headers)
        if response.status_code == 200:
            with st.chat_message("assistant"):
                st.markdown(response.json()['receive'])
        else:
            with st.chat_message("assistant"):
                st.error("Error")

        st.session_state.messages.append({'role': 'assistant', 'text': response.json()['message']})


def create_session(prompt):

    params = {
        'name': prompt
    }
    headers = {
        'Authorization': f'Bearer {st.session_state["access_token"]}',
        'Content-Type': 'application/json'
    }
    api_url = f"http://localhost:3000/sessions"

    response = requests.post(api_url, json=params, headers=headers)
    if response.status_code == 200:
        return response.json()['name']
    else:
        st.error("Error")

with st.sidebar:
    st.write("History....")
    if st.button("New chat", key="new_chat"):
        st.session_state.messages = []


if not prompt:
    default_page()
if not "messages" in st.session_state:
    default_page()
else:
    new_chat()
