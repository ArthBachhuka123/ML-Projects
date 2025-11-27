import streamlit as st 
from main import chatbot, retrieve_all_threads, generate_title, get_all_thread_titles
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
import uuid

st.header("LangGraph Chatbot")

# ---------------------------helping functions ---------------------

def generate_thread():
    thread_id = uuid.uuid4()
    return thread_id

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def reset_chat():
    thread_id = generate_thread()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id=thread_id)
    st.session_state["message_history"] = []

def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable":{"thread_id":thread_id}})
    return state.values.get("messages", [])

#------------------------------------------------------------------





# ---------------------- SessionStates -----------------------

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

add_thread(st.session_state["thread_id"])

# -------------------- SIDEBAR UI ---------------------------------

st.sidebar.title("LangGraph Chatbot")

button = st.sidebar.button("New Chat")

if button:
    reset_chat()

st.sidebar.header("My Conversations")

thread_titles = get_all_thread_titles()

for thread in st.session_state["chat_threads"][::-1]:
    title = thread_titles.get(str(thread), "New Chat")
    if st.sidebar.button(title,key=str(thread)):
        st.session_state["thread_id"] = thread
        messages = load_conversation(thread_id=thread)
        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg,HumanMessage) else "assistant"
            temp_messages.append({"role":role, "content":msg.content})
        st.session_state["message_history"] = temp_messages



#---------------------------------------------------------------



#--------------------------------------------------------------

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


user_input = st.chat_input("Type your message")

if user_input:

    thread_id_str = str(st.session_state["thread_id"])
    thread_titles = get_all_thread_titles() 

    if thread_id_str not in thread_titles:
        generate_title(user_input, thread_id_str)

    st.session_state["message_history"].append({"role":"user","content":user_input})

    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {"configurable":{"thread_id":st.session_state["thread_id"]}
            ,"metadata":{"thread_id":st.session_state["thread_id"]},
            "run_name":"PROJECT_RUN"}
    
# Assistant streaming block
    with st.chat_message("assistant"):

        def stream_only_ai():
            for item in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # item may be (chunk, metadata) OR just chunk
                if isinstance(item, tuple):
                    message_chunk, metadata = item
                else:
                    message_chunk = item

                if not isinstance(message_chunk, AIMessage):
                    continue

                content = message_chunk.content

                # Normalize content to string
                if isinstance(content, list):
                    text_parts = []
                    for piece in content:
                        if isinstance(piece, dict) and "text" in piece:
                            text_parts.append(piece["text"])
                    content = "".join(text_parts)

                if not isinstance(content, str):
                    content = str(content)

                yield content

        ai_message = st.write_stream(stream_only_ai())

# Save final message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message or ""}
    )

        