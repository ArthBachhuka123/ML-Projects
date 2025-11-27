
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_core.tools import tool, StructuredTool
from dotenv import load_dotenv
from typing import TypedDict, Optional, Annotated
from pydantic import BaseModel, Field
import os, requests
import sqlite3

load_dotenv()



model = ChatGroq( model = "llama-3.3-70b-versatile")

search_tool = DuckDuckGoSearchRun()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

class StockInput(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol")

def get_stock_price(symbol: str):
    url = (
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE"
        f"&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    )
    return requests.get(url).json()

get_stock_price = StructuredTool.from_function(
    func=get_stock_price,
    args_schema=StockInput,
    name="get_stock_price",
    description="Retrieve live stock price using AlphaVantage."
)

tools = [search_tool, get_stock_price]
model_with_tools = model.bind_tools(tools)
conn = sqlite3.connect("ChatBot.db", check_same_thread= False)
checkpointer = SqliteSaver(conn=conn)

def save_thread_title(thread_id, title):
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS thread_titles (thread_id TEXT PRIMARY KEY, title TEXT)"
    )
    cursor.execute(
        "INSERT OR REPLACE INTO thread_titles (thread_id, title) VALUES (?, ?)",
        (str(thread_id), title)
    )
    conn.commit()


def build_chatbot(): 
    class ChatState(MessagesState):
        pass
    
    def chat_node(state: ChatState):
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    tool_node = ToolNode(tools)


    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile(checkpointer=checkpointer)
    return chatbot

chatbot= build_chatbot()


def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        cp = checkpoint[0]  # <-- actual checkpoint dict
        all_threads.add(cp["configurable"]["thread_id"])
    return list(all_threads)


def generate_title(message, thread_id):
    prompt = PromptTemplate(
        template = "generate a title(max 5 words) for this user message{message}",
        input_variables=["message"]
    )
    chain = prompt | model 
    response = chain.invoke({"message":message})
    title = response.content.strip()
    save_thread_title(thread_id=thread_id, title=title)
    return title

def get_all_thread_titles():
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS thread_titles (thread_id TEXT PRIMARY KEY, title TEXT)"
    )
    rows = cursor.execute(
        "SELECT thread_id, title FROM thread_titles"
    ).fetchall()
    return {row[0]: row[1] for row in rows}


    
