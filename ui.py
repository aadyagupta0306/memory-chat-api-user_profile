import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

# --- Sidebar ---
with st.sidebar:
    st.title("your threads")
    st.caption("copy an ID and use Get Thread to load it")

    res = requests.get(f"{API_URL}/threads")
    if res.status_code == 200:
        all_threads = res.json().get("threads", [])
        if all_threads:
            for t in all_threads:
                st.markdown(f"• `{t}`")
        else:
            st.info("no threads yet")
    else:
        st.error("couldn't load threads")

    if st.button("refresh"):
        st.rerun()

# --- Main ---
st.title("💬 hey Riya.")
st.caption("your ai already knows you. just talk.")

st.subheader("thread management")
thread_id = st.text_input("Thread ID", placeholder="e.g. work, personal, agency...")

col1, col2 = st.columns(2)

with col1:
    if st.button("Create Thread"):
        if thread_id:
            res = requests.post(f"{API_URL}/threads/{thread_id}")
            if res.status_code == 200:
                st.success(f"thread '{thread_id}' created!")
                st.rerun()
            else:
                st.error(res.json().get("detail", "something went wrong"))
        else:
            st.warning("enter a thread id first")

with col2:
    if st.button("Get Thread"):
        if thread_id:
            res = requests.get(f"{API_URL}/threads/{thread_id}")
            if res.status_code == 200:
                st.session_state.active_thread = thread_id
                st.session_state.messages = res.json().get("messages", [])
                st.success(f"loaded '{thread_id}'!")
            else:
                st.error(res.json().get("detail", "thread not found"))
        else:
            st.warning("enter a thread id first")

st.divider()

if "active_thread" in st.session_state:
    st.info(f"📂 active thread: **{st.session_state.active_thread}**")

    st.subheader("conversation")
    if st.session_state.messages:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**🧑 Riya:** {msg['content']}")
            else:
                st.markdown(f"**🤖 ai:** {msg['content']}")
    else:
        st.info("nothing here yet. say something!")

    st.divider()

    user_message = st.text_input("say something", placeholder="anything...")

    if st.button("send"):
        if user_message:
            res = requests.post(
                f"{API_URL}/threads/{st.session_state.active_thread}/messages",
                json={"message": user_message}
            )
            if res.status_code == 200:
                data = res.json()
                st.session_state.messages.append({"role": "user", "content": user_message})
                st.session_state.messages.append({"role": "assistant", "content": data["reply"]})
                st.rerun()
            else:
                st.error(res.json().get("detail", "something went wrong"))
        else:
            st.warning("type something first")
else:
    st.info("create a new thread or load an existing one to start")

#run using following commands
# python3 -m streamlit run ui.py
