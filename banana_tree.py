from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import create_react_agent

model = ChatOpenAI(model="gpt-4o")

# ==========================================
# 1. SUB-AGENT A: Built using `create_react_agent`
# ==========================================
# This prebuilt agent handles quick or specific tasks
prebuilt_worker = create_react_agent(model, tools=[])


@tool
def search_subagent(query: str) -> str:
  """Use this tool for quick lookups, facts, or search tasks."""
  response = prebuilt_worker.invoke({"messages": [("user", query)]})
  return response["messages"][-1].content


# ==========================================
# 2. SUB-AGENT B: Built using `StateGraph` builder
# ==========================================
# This custom builder handles complex multi-step workflows
custom_builder = StateGraph(MessagesState)


def custom_worker_node(state: MessagesState):
  # Perform custom multi-step logic here
  response = model.invoke([
      (
          "system",
          (
              "You are a specialized analytical worker inside a custom graph"
              " sub-agent."
          ),
      )
  ] + state["messages"])
  return {"messages": [response]}


custom_builder.add_node("worker", custom_worker_node)
custom_builder.add_edge(START, "worker")
custom_builder.add_edge("worker", END)

# Compile the custom graph
compiled_custom_subagent = custom_builder.compile()


# Wrap the compiled custom graph as a tool so the supervisor can call it like any other tool
@tool
def analytical_subagent(query: str) -> str:
  """Use this tool for deep data analysis and custom multi-step workflows."""
  response = compiled_custom_subagent.invoke({"messages": [("user", query)]})
  return response["messages"][-1].content


# ==========================================
# 3. SUPERVISOR: Built using `create_react_agent`
# ==========================================
# Combine both sub-agent tools into the supervisor's toolbelt
supervisor_tools = [search_subagent, analytical_subagent]

# Create the supervisor agent with a prompt that guides its delegation strategy
supervisor_agent = create_react_agent(
    model,
    tools=supervisor_tools,
    prompt=(
        "You are an executive supervisor agent. Your job is to analyze the"
        " user's request, delegate it to the appropriate sub-agent tool"
        " (search_subagent or analytical_subagent), and synthesize their"
        " answers into a final response."
    ),
)

# ==========================================
# Running the System
# ==========================================
if __name__ == "__main__":
  # Example execution
  result = supervisor_agent.invoke({
      "messages": [
          (
              "user",
              "Can you run a deep analytical check on our quarterly metrics?",
          )
      ]
  })

  print(result["messages"][-1].content)