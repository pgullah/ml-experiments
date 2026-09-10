from uuid import uuid4

import streamlit as st

from app.agent import Agent
from app.common.config import AppSettings
from app.planner import TravelPlanner

st.set_page_config(
    page_title="AI Travel Agent",
    page_icon="✈️",
)

st.title("AI Travel Agent")


def create_agent() -> Agent:
    settings = AppSettings()  # pyright: ignore[reportCallIssue]
    planner = TravelPlanner(settings)
    return Agent(planner)


if "agent" not in st.session_state:
    st.session_state.agent = create_agent()
    st.session_state.thread_id = str(uuid4())
    st.session_state.messages = []

if st.sidebar.button("New conversation"):
    st.session_state.agent = create_agent()
    st.session_state.thread_id = str(uuid4())
    st.session_state.messages = []
    st.rerun()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Where would you like to travel?"):
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Planning your trip..."):
                response = st.session_state.agent.chat(
                    prompt,
                    thread_id=st.session_state.thread_id,
                )
        except ValueError as error:
            response = str(error)

        st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )
