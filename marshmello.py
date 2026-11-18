import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage

app = FastAPI()

# 1. Set up a persistent SQLite checkpointer database
# (Using check_same_thread=False allows FastAPI's async workers to access it)
sqlite_conn = sqlite3.connect("agent_state.db", check_same_thread=False)
memory_checkpointer = SqliteSaver(sqlite_conn)

# 2. Initialize the model and agent once globally
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
# Pass the checkpointer directly into the agent/graph builder
agent_executor = create_react_agent(model=model, tools=[], checkpointer=memory_checkpointer)


class ChatRequest(BaseModel):
    user_id: str  # Used as the thread_id to isolate user sessions
    prompt: str


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # 3. Define the thread configuration for this specific user session
        config = {"configurable": {"thread_id": request.user_id}}
        
        # 4. Invoke the agent. SQLite automatically loads/saves the state for this thread_id.
        input_message = {"messages": [HumanMessage(content=request.prompt)]}
        
        # Using ainvoke for asynchronous performance under concurrent traffic
        response = await agent_executor.ainvoke(input_message, config=config)
        
        # Extract the final message content safely
        messages = response.get("messages", [])
        reply = messages[-1].content if messages else "No response generated."

        return {"user_id": request.user_id, "response": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))