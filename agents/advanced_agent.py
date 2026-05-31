from typing import Dict, Any
from langgraph.graph import StateGraph, END, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
from .base import BaseAgent
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver


class AdvancedAgent(BaseAgent):
    """
    Advanced Agent using LangGraph.
    Exposed to all available tools and decides what to do.
    """
    
    def __init__(self, llm_client, short_term_memory, tools=[]):
        super().__init__(
            llm_client=llm_client,
            short_term_memory=short_term_memory,
            tools=tools
        )
        self.llm_client = llm_client
        self.short_term_memory = short_term_memory
        self.tools = tools
        self.graph = self._build_graph()

    
    def _build_graph(self):
        """Build the state graph for the agent."""
        graph = StateGraph(MessagesState)
        graph.add_node("agent", self._agent)
        if len(self.tools) > 0:
            self.llm_client = self.llm_client.bind_tools(self.tools)
            tool_node = ToolNode(self.tools)
            graph.add_node("tool_node", tool_node)
            graph.add_edge(START, "agent") 
            graph.add_conditional_edges(
                "agent",
                tools_condition,
                {
                    "tools": "tool_node",
                    END: END
                }
            )           
            graph.add_edge("tool_node", "agent")  
        else:
            graph.add_edge(START, "agent")
            graph.add_edge("agent", END)
        
        conn = sqlite3.connect("./databases/checkpoints.db", check_same_thread=False)
        checkpointer = SqliteSaver(conn)

        app = graph.compile(checkpointer=checkpointer)
        return app

    def _agent(self, state: MessagesState) -> MessagesState:
        response = self.llm_client.invoke(state["messages"])
        return {"messages": [response]}
    
    def run(self, user_query: str) -> Dict[str, Any]:
        
        if len(self.tools) > 0:
            prompt = f"""
            You are an AI agent with access to conversation history, memory, retrieval, web, and utility tools.

Instructions:

* Use the conversation history before responding.
* Check available tools when helpful instead of assuming.
* Use retrieval/web/search tools for missing or external information.
* Use memory tools to:

  * retrieve useful user context before answering.
  * store important long-term user facts, preferences, projects, or goals when relevant.
* Avoid storing temporary or sensitive information unless explicitly requested.
* Use query rewriting/search optimization tools when needed.
* Keep responses concise, accurate, and context-aware.
* Avoid asking for information already present in the history or memory.

            """
            system_msg = SystemMessage(content=prompt)
        else:
            system_msg = SystemMessage(content="You are a helpful assistant.")

        messages = {"messages": [system_msg, HumanMessage(content=user_query)]}
        config = {
        "configurable": {
        "thread_id": self.short_term_memory.session_id,
            }
        }
        result = self.graph.invoke(messages, config=config)
        answer = result["messages"][-1].content if result["messages"] else "No response"
        self.short_term_memory.add_message("user", user_query)
        self.short_term_memory.add_message("assistant", answer)
        return {
            "answer": answer,
            "agent_type": "advanced",
        }