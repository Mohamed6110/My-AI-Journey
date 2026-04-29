from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from Tool import *
from config import *
from agent_tools import *



# ================================================================
# SYSTEM PROMPT
# ================================================================

TEACHER_SYSTEM_PROMPT =  """You are **Teacher**, an Advanced Educational Intelligence Agent with the following authoritative identity:

- **Primary Domain**: Certified Educational Technologist & Master Instructional Designer with 15+ years experience
- **Specialization**: K-12 and Higher Education curriculum development, differentiated instruction, and evidence-based pedagogical strategies
- **Certifications**: PhD in Learning Sciences, Certified in Universal Design for Learning (UDL), Qualified in Assessment Design
- **Tone & Communication Style**:
  * Professional yet approachable - model effective teaching communication
  * Precise and evidence-based - cite pedagogical frameworks when relevant
  * Adaptive - adjust complexity based on student grade level and context
  * Collaborative - support teachers as partners in education, not replacements
  * Empathetic - understand students' needs and concerns
Using Tavily search tool, include relevant examples, case studies, and real-world applications to illustrate the concepts.,
Ensure the knowledge base is well-structured and organized for easy reference.,
Based on the information you generated, add a summary section at the end that highlights the key takeaways and important points.
create at leasts 5 questions based on the information you generated.to make sure the student understand the concepts well.and then go to next topic
**Do not forget to include a section for further reading and exploration with links to relevant resources.
 use Composio tool to Delegate tasks that require external tools and integrations via Composio.
    Use for: creating forms, sending emails, managing files, calendar events,
    spreadsheets, or any task requiring third-party service integration create slides or any external tools.
"""







# ================================================================
# AGENT — load_skill added to tools
# ================================================================

teacher_agent = create_agent(
    model=model,
    tools=[
        search_tool,
        simplify_explanation,
        generate_examples,
        create_quiz,
        evaluate_answer,
        summarize_content,
        composio_agent_tool,
        ask_planner,ask_teacher_assistant
        
              
    ],
    system_prompt=TEACHER_SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),
)


# ================================================================
# CHAT LOOP
# ================================================================

config = {"configurable": {"thread_id": "teacher_chat_1"}}

print("--- Teacher Agent Chat (Type 'exit' to stop) ---")
# def run():
#     while True:
#         user_input = input("User: ")

#         if user_input.lower() in ["exit", "quit", "q"]:
#             print("Chat ended.")
#             break

#         inputs = {"messages": [("user", user_input)]}

#         for chunk in teacher_agent.stream(
#             inputs, config=config, stream_mode="values"
#         ):
#             final_message = chunk["messages"][-1]

#         final_message.pretty_print()

#         print("\n")

# if __name__=="__main__":
#     run()
# import sys
# import time

# def run():
#     while True:
#         user_input = input("User: ")

#         if user_input.lower() in ["exit", "quit", "q"]:
#             print("Chat ended.")
#             break

#         inputs = {"messages": [("user", user_input)]}

#         # Keep track of the message content
#         final_text = ""

#         for chunk in teacher_agent.stream(
#             inputs, config=config, stream_mode="values"
#         ):
#             final_message = chunk["messages"][-1]
#             final_text = final_message.content  # Extract string content

#         # Custom typewriter output
#         print("Assistant: ", end="", flush=True)
#         for char in final_text:
#             sys.stdout.write(char)
#             sys.stdout.flush()
#             time.sleep(0.02)  # Adjust speed here (lower = faster)
        
#         print("\n")

# if __name__=="__main__":
#     run()




