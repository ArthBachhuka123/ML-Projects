from langgraph.graph import StateGraph, START, END, MessagesState
# from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Send
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import Field, BaseModel
from dotenv import load_dotenv
from typing import List, Annotated, TypedDict
import operator

from streamlit import title

load_dotenv() 

class Task(BaseModel):
    id: int
    title: str
    brief: str = Field(... , description="What to cover")

class Plan(BaseModel):
    blog_title: str
    tasks: List[Task]

class State(TypedDict):
    topic: str 
    plans: Plan
    sections: Annotated[List[str], operator.add]
    final: str

llm = ChatGroq( model = "llama-3.3-70b-versatile")

parser1 = PydanticOutputParser(pydantic_object=Plan)

def orchestrator(state: State):
    prompt = PromptTemplate(
        template=""""Create a blog plan with 5-7 sections on the topic: {topic}.
        Format the response as per the {format_instructions}""",
        input_variables=["topic"],
        partial_variables={"format_instructions":parser1.get_format_instructions()}
    )

    plan = llm.invoke(prompt.format(topic = state["topic"]))
    parsed_plan = parser1.parse(plan.content)
    return {"plans": parsed_plan}

def fanout(state: State):
    return [Send("worker", {"task": task , "topic": state["topic"], "plan": state["plans"]}) for task in state["plans"].tasks]

def worker(payload: dict):
    task = payload["task"]
    topic = payload["topic"]
    plan = payload["plan"] 

    blog_title= plan.blog_title

    section_md = llm.invoke([
        SystemMessage(content="Write a clean blog markdown section."),
        HumanMessage(content=(f"Blog:{blog_title}\n"
                    f"Section_title: {task.title}"
                    f"Brief: {task.brief}"
                    f"Topic: {topic}")
                )
    ]).content.strip() 

    return {"sections": [section_md]}

from pathlib import Path

def reducer(state: State):
    title = state["plans"].blog_title
    body = "\n\n".join(state["sections"]).strip()
    final_md = f"#{title}\n\n{body}"

    filename = title.lower().replace(" ", "_") + ".md"
    output_path = Path(filename)
    output_path.write_text(final_md, encoding= "utf-8")

    return {"final": final_md}


def build_graph():
    graph = StateGraph(state_schema=State)

    graph.add_node("orchestrator", orchestrator)
    graph.add_node("worker", worker)
    graph.add_node("reducer", reducer)

    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges("orchestrator", fanout, ["worker"])
    graph.add_edge("worker", "reducer")
    graph.add_edge("reducer", END)

    agent = graph.compile()
    return agent 

agent = build_graph()


output = agent.invoke({"topic": "Blog on Chinaman bowler in Cricket"})



