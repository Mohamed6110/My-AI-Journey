import sqlite3
import pandas as pd
import time
from datetime import datetime,timedelta
from crewai import Agent,Task,LLM,Crew,Process
from crewai_tools import CodeInterpreterTool
from crewai.tools import tool
import random
import sys
import streamlit as st
import re
import os
from datetime import datetime as _dt
model=LLM(model="ollama_chat/qwen3.5:397b-cloud ",
          base_url="http://localhost:11434",stream=True)

# define tools for database interaction
@tool("inspect_data")
def inspect_data()->list:
    """"Return List of Table names in database"""
    from sqlalchemy import create_engine,inspect
    conn=create_engine("sqlite:///sakila_master.db")
    return inspect(conn).get_table_names()


@tool("search_in_data")
def search_in_data(query:str)->str:
    """Execute SQL query and return results as markdown table
    Args:
        query: SQL query to execute on Database
        
        Returns:
        - Markdown table of results
        """
    import sqlite3
    import pandas as pd
    conn=sqlite3.connect("sakila_master.db")
    df=pd.read_sql_query(query,conn)
    return df.to_markdown()



sql_agent=Agent(
    role="SQL Developer",
    goal="Search in database about data and return results to user using sqlite",
    backstory="You are professinal sql developer that write efficient select sqlite queries to retireve data from DB, inspect database before writing sql" ,
    llm=model,
    tools=[search_in_data,inspect_data],
    

)
python_agent=Agent(
    role="Python Developer",
    goal="Visualize the data passed to you by sql agent using python and return the visualization to user based on the data passed to you and the question asked by user",
    backstory="You are a professional python developer that write efficient code to visualize data using plotly library and other python visualization libraries",
    llm=model,
    tools=[CodeInterpreterTool(unsafe_mode=True)],
    

)
story_telling_agent=Agent(
    role="Story Teller,Executive Report Writer",
    goal="Write a polished, structured executive report from the analysis findings and Tell a story about the data and insights you get from sql agent and visualization agent",
    backstory="""You are a professional story teller that write engaging 
                stories about data insights and visualization to help user understand 
                the data better and make informed decisions""",
    llm=model,
    tools=[],
    
)

## Create Tasks
def run_pipeline(user_prompt):
    search_task=Task(
        description=f"Search by {user_prompt} and return results in markdown format",
        expected_output="Markdown table of search Results with clear labels and descriptions of each column",
        agent =sql_agent
    )
    visualization_task=Task(
        description="Visualize the data passed to you if exists and save the visualization in png format where plot details are ",
        expected_output="Visualization of data in png format and save it and show the visualization to user ",
        agent=python_agent
    )
    _TODAY = _dt.now().strftime("%B %d, %Y")
    story_telling_task=Task(
    description=(
        f"Generate a complete executive-level Business Intelligence report dated {_TODAY}.\n\n"

        "You are a Senior BI Analyst. Your job is to transform data and visual outputs into "
        "clear, actionable business insights.\n\n"

        "## Required Sections:\n"
        "1. Executive Summary (concise, high-impact)\n"
        "2. Data Sources (what data was used)\n"
        "3. Key Findings (bullet points)\n"
        "4. Analysis & Insights (deep interpretation)\n"
        "5. Visualizations (embed all charts with explanation)\n"
        "6. Business Impact (risks & opportunities)\n"
        "7. Recommendations (actionable & prioritized)\n"
        "8. Conclusion\n\n"

        "## Critical Instructions:\n"
        "- Interpret data, do NOT just describe it.\n"
        "- Every visualization must be explained and linked to an insight.\n"
        "- Focus on business value and decision-making.\n"
        "- Avoid technical jargon.\n"
        "- Ensure logical flow and clarity.\n\n"

        "## Output Format:\n"
        "- Clean Markdown\n"
        "- Professional formatting\n"
        "- Embed visualization file names (PNG)\n"
        "- Ready for executive presentation\n"
    ),
    expected_output=(
        "A fully structured, professional BI report saved in a PDF format, "
        "including insights, embedded visualizations, and actionable recommendations."
    ),
    agent=story_telling_agent
)
    crew=Crew(
        agents=[sql_agent,python_agent,story_telling_agent],
        tasks=[search_task,visualization_task,story_telling_task],
        process=Process.sequential,
        
    )
    ## Create Crew and add tasks to it
    return crew.kickoff()

# --- 4. Interactive Chat CLI ---
if __name__ == "__main__":
    print("\n--- CrewAI Autonomous Data Pipeline CLI ---")
    while True:
        user_req = input("\nHow can I help with your data today? (exit to quit): ")
        if user_req.lower() in ['exit', 'quit']:
            break
            
        result = run_pipeline(user_req)
        print("\n" + "="*30)
        print("FINAL RESPONSE FROM AGENTS:")
        print("="*30)
        for char in str(result):
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.01)
        print("\n" + "="*30)