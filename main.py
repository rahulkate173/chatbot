### here is the backend for chatbot
### START -> Chat -> End 
### This as SqlLite as checkpointer with streaming implemented 

from dotenv import load_dotenv
from langgraph.graph import START,END,StateGraph
from langchain_core.messages import HumanMessage,SystemMessage,BaseMessage
from langchain_groq import ChatGroq
from typing import Annotated,TypedDict,List,Sequence
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import operator
from rich import print 
import sqlite3
load_dotenv()

## create database connection : Sqllite
conn = sqlite3.connect("chatbot.db",check_same_thread=False) # to get multithread 
## creating llm 
model = ChatGroq(
    model = "llama-3.3-70b-versatile",
    temperature = 0.2
)

## creating Statedict
class ChatModel(TypedDict):
    messages : Annotated[Sequence[BaseMessage],operator.add]

## creating graph 
def chat_interface(state:ChatModel):
    output = model.invoke(state.get("messages",[]))
    return {"messages": [output]}

graph =  StateGraph(ChatModel)
graph.add_node("chat",chat_interface)

graph.add_edge(START,"chat")
graph.add_edge("chat",END)

# checkpointer 
checkpointer = SqliteSaver(conn)
config = {"configurable": {"thread_id": "1"}} # here the thread_id can be dynamic 

workflow = graph.compile(checkpointer=checkpointer)
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