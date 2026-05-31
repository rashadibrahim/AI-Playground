from app.builder import AppBuilder
import os
from typing import List
import sqlite3


def load_sessions() -> List[tuple]:
    db_path = "./databases/short_term.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT session_id, session_name FROM messages")
        sessions = cursor.fetchall()
        conn.close()
        return sessions
    else:
        return []
    
    
if __name__ == "__main__":
    model_options = ["qwen/qwen3-32b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    builder = AppBuilder()
    
    os.system("cls" if os.name == "nt" else "clear")
    
    print("Welcome to the RAG Agent Playground!")
    choice = input("Choose agent type (simple, rag_memory, advanced): ").strip()
    
    if choice not in ["simple", "rag_memory", "advanced"]:
        print("Invalid choice, defaulting to 'simple'")
        choice = "simple"
    
    
    builder.with_agent(choice)
    
    
    print("Models available:")
    for idx, model in enumerate(model_options):
        print(f"{idx+1}. {model}")
    model_choice = input(f"Choose a model (1-{len(model_options)}): ").strip()
    try:
        model_idx = int(model_choice) - 1
        if 0 <= model_idx < len(model_options):
            if model_idx == 2 and choice == "advanced":
                print("The selected model may not perform well with the advanced agent. Defaulting to 'openai/gpt-oss-120b'.")
                builder.with_model("openai/gpt-oss-120b")
            else:
                builder.with_model(model_options[model_idx])
        else:
            print("Invalid model choice, defaulting to first model.")
    except ValueError:
        print("Invalid input, defaulting to first model.")
    
    if choice in ["rag_memory", "advanced"]:
        print("""Do you have any new documents inside the 'documents' folder that you want to load into the RAG pipeline? (y/n)""")
        load_docs = input().strip().lower() == "y"
        if load_docs:
            builder.with_new_documents()

    
    load_session = input("Do you wanna load a previous session? (y/n): ")
    if load_session.strip().lower() == "y":
        sessions = load_sessions()
        if sessions:
            print("Available sessions:")
            for idx, (sid, sname) in enumerate(sessions):
                print(f"{idx+1}. {sname} (ID: {sid})")
            session_choice = input(f"Choose a session to load (1-{len(sessions)}): ").strip()
            try:
                session_idx = int(session_choice) - 1
                if 0 <= session_idx < len(sessions):
                    sid, sname = sessions[session_idx]
                    builder.with_session_info(session_id=sid, session_name=sname)
                else:
                    print("Invalid session choice, starting new session.")
                    sname = input("Enter a new session name: ")
                    builder.with_session_info(session_name=sname)
            except ValueError:
                print("Invalid input, starting new session.")
                sname = input("Enter a new session name: ")
                builder.with_session_info(session_name=sname)
        else:
            print("No previous sessions found, starting new session.")
            sname = input("Enter a new session name: ")
            builder.with_session_info(session_name=sname)
    
    """
    NOTE:
    *new tools can be added to the builder by calling the with_tools method and passing a list of tool instances.
    otherwise, if the advanced agent is selected and no tools are provided, it will default to using all available tools in the tools module.
    
    *there are 2 strategies for document embedding: 
    1- parent_child: where the parent document is embedded as a whole and the child chunks are embedded separately.
    2- summary: where the summary of each document is embedded.
    
    the code uses the parent_child strategy by default, 
    but you can switch to summary by changing the: "strategy_type" parameter to "summary" in RAGPipeline class. 
    """
    app = builder.build()
    
    
    os.system("cls" if os.name == "nt" else "clear")
    app.run_interactive()

