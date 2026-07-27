### here is the backend for chatbot
### START -> Chat -> End 
### This as SqlLite as checkpointer with streaming implemented 

from dotenv import load_dotenv
from langgraph.graph import START,END,StateGraph
from langchain_core.messages import HumanMessage,SystemMessage,BaseMessage
from langchain_groq import ChatGroq
from typing import Annotated,TypedDict,List,Sequence
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import operator
from backend_tools import calculator , search_tool , get_stock_price
from rich import print 
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode , tools_condition
import sqlite3
load_dotenv()

## create database connection : Sqllite
conn = sqlite3.connect("chatbot.db",check_same_thread=False) # to get multithread 
## creating llm 
model = ChatGroq(
    model = "qwen/qwen3.6-27b",
    temperature = 0.2
)

tools = [calculator,search_tool,get_stock_price]
tool_node = ToolNode(tools)
llm_with_tools = model.bind_tools(tools)

## creating Statedict
class ChatModel(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

## creating graph 
def chat_interface(state:ChatModel):
    output = llm_with_tools.invoke(state.get("messages",[]))
    return {"messages": [output]}


graph =  StateGraph(ChatModel)
graph.add_node("chat",chat_interface)
graph.add_node("tools",tool_node) # the tool node 

graph.add_edge(START, "chat")
graph.add_conditional_edges("chat",tools_condition)
graph.add_edge('tools', 'chat')
## default will go to end

# checkpointer 
checkpointer = SqliteSaver(conn)
config = {"configurable": {"thread_id": "1"}} # here the thread_id can be dynamic 

def create_workflow():
    workflow = graph.compile(checkpointer=checkpointer)
    return workflow

workflow = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)

while True :
    message = input("User: ")
    if message.lower() in ("break","exit","done"):
        break
    initial_state = {
        "messages": [HumanMessage(message)]
    }
    # print(initial_state)
    # response = workflow.invoke(initial_state,config) # to identify the thread
    for chunk in workflow.stream(
        initial_state, config, stream_mode="messages", version="v2"
    ):
        if chunk["type"] == "messages":
            msg_chunk, metadata = chunk["data"]
            # Print each token as it arrives
            if msg_chunk.content:
                print(msg_chunk.content, end="", flush=True) 
    print() # normal 
    
    
    