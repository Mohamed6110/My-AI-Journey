
from langchain.tools import tool
from config import *
@tool
def search_tool(query: str) -> str:
    """
    Search for current, real-world information on any topic.

    Use this for:
    - Recent developments, news, or updates
    - Verifying facts that may have changed
    - Finding real examples, libraries, or frameworks

    Do NOT use for timeless concepts (e.g., 'what is a variable') —
    answer those directly from knowledge.

    Args:
        query: A specific, focused search query (3-8 words ideal)
    """
    result = tavily_client.search(query)
    return str(result.get("results", result))


@tool
def simplify_explanation(concept: str, student_level: str) -> str:
    """
    Simplify a complex concept into a beginner-friendly explanation.

    Use when the student is confused or explicitly asks for a simpler version.

    Args:
        concept: The specific concept to simplify
        student_level: 'beginner', 'intermediate', or 'advanced'

    Returns:
        Plain-language explanation with analogy and concrete example
    """
    return (
        f"Simplified explanation of '{concept}' for {student_level} level:\n"
        f"[Analogy] + [Plain-language breakdown] + [Concrete example]"
    )


@tool
def generate_examples(concept: str, example_type: str, student_level: str) -> str:
    """
    Generate targeted examples to reinforce understanding of a concept.

    Use after explaining a concept to make it concrete.

    Args:
        concept: The topic to generate examples for
        example_type: 'real-world', 'code', 'analogy', or 'all'
        student_level: 'beginner', 'intermediate', or 'advanced'

    Returns:
        2-3 examples matched to the student's level and requested type
    """
    return (
        f"{example_type} examples for '{concept}' ({student_level} level):\n"
        f"1. Real-world scenario\n2. Simple analogy\n3. Code example (if applicable)"
    )


@tool
def create_quiz(concept: str, difficulty: str, num_questions: int) -> str:
    """
    Create a multiple-choice quiz to test understanding of a concept.

    Use after teaching a concept to verify retention before moving on.

    Args:
        concept: The topic to quiz on
        difficulty: 'easy', 'medium', or 'hard'
        num_questions: Number of questions (1-5 recommended)

    Returns:
        MCQ quiz with answer key — present questions one at a time
        after end of session create final quiz using composio_tools
    """
    return f"""
Quiz on '{concept}' ({difficulty}, {num_questions} questions):

Q1. [Question about {concept}]?
A) Option A
B) Option B
C) Option C  ← correct
D) Option D

[Answer Key: hidden until student answers]
"""


@tool
def evaluate_answer(
    student_answer: str,
    correct_answer: str,
    concept: str
) -> str:
    """
    Evaluate a student's answer and provide constructive feedback.

    Use immediately after the student responds to a quiz question.

    Args:
        student_answer: What the student submitted
        correct_answer: The expected correct answer
        concept: The concept being tested (for targeted feedback)

    Returns:
        Pass/fail verdict + explanation of why + hint if wrong
    """
    if student_answer.strip().lower() == correct_answer.strip().lower():
        return f"✅ Correct! You've understood '{concept}' well."
    return (
        f"❌ Not quite. The correct answer is '{correct_answer}'.\n"
        f"Hint: Review the core idea of '{concept}' — "
        f"focus on [key principle]. Try once more?"
    )


@tool
def summarize_content(text: str, focus: str) -> str:
    """
    Summarize a block of content with a specific focus area.

    Use when the student asks for a recap or before ending a session.

    Args:
        text: The content to summarize
        focus: What aspect to emphasize (e.g., 'key concepts', 'steps', 'formulas')

    Returns:
        Concise summary with key takeaways and further reading links
    """
    return (
        f"Summary (focus: {focus}):\n"
        f"{text[:300]}...\n\n"
        f"Key Takeaways:\n- [Point 1]\n- [Point 2]\n- [Point 3]\n\n"
        f"Further Reading: [relevant links]"
    )


@tool
def generate_exercise(topic: str) -> str:
    """Generate structured exercises"""
    return f"""
[EXERCISE PLAN: {topic}]

1. Basic:
- Explain {topic} in your own words

2. Applied:
- Give a real-world example of {topic}

3. Challenge:
- Solve a problem using {topic}
"""

@tool
def case_study(topic: str) -> str:
    """Generate case study"""
    return f"""
[CASE STUDY: {topic}]

- Context: Real-world use of {topic}
- Problem: What challenge is solved?
- Analysis: How {topic} is applied
"""

@tool
def role_play(topic: str) -> str:
    """Generate role-play scenario"""
    return f"""
[ROLE PLAY: {topic}]

You are in a real-world situation using {topic}.

Task:
- Identify problem
- Apply concept
- Explain your decision
"""

@tool
def evaluate_response(answer: str) -> str:
    """Evaluate student answer"""
    return f"""
[FEEDBACK]

Answer:
{answer}

- Understanding: Weak / Medium / Strong
- Missing points: ...
- Improvement: Refine your reasoning + add examples
"""

@tool
def search_tool(query: str) -> str:
    """
    Search for current, real-world information on any topic.

    Use this for:
    - Recent developments, news, or updates
    - Verifying facts that may have changed
    - Finding real examples, libraries, or frameworks

    Do NOT use for timeless concepts (e.g., 'what is a variable') —
    answer those directly from knowledge.

    Args:
        query: A specific, focused search query (3-8 words ideal)
    """
    return tavily_client.search(query)
@tool
def create_learning_plan(topic: str, level: str) -> str:
    """
    Creates a structured, dependency-aware learning roadmap.

    Args:
        topic: The subject the student wants to learn
        level: Student's current level — 'beginner', 'intermediate', or 'advanced'

    Returns:
        Ordered steps with goals, durations, prerequisites, and success criteria
    """
    return f"Roadmap for '{topic}' at {level} level"


@tool
def define_milestones(topic: str, level: str) -> str:
    """
    Defines measurable milestones and checkpoints for a learning plan.

    Args:
        topic: The subject being learned
        level: Student's current level

    Returns:
        Milestone list with unlock conditions and success criteria
    """
    return f"Milestones for '{topic}' at {level} level"


@tool
def assign_practice(topic: str, step: str, difficulty: str) -> str:
    """
    Assigns hands-on exercises for a specific step in the learning plan.

    Args:
        topic: Main subject
        step: Specific concept the student just studied
        difficulty: 'easy', 'medium', or 'hard' — must match student level

    Returns:
        Practice task with description, expected output, and success condition
    """
    return f"{difficulty} practice task for '{step}' in '{topic}'"


@tool
def evaluate_progress(topic: str, step: str, student_response: str) -> str:
    """
    Evaluates student performance at a checkpoint and recommends next action.

    Args:
        topic: Main subject
        step: Concept being evaluated
        student_response: Student's answer or submitted work

    Returns:
        Score (0-100), detected weak points, and next action:
        'advance' | 'reinforce' | 'simplify'
    """
    return f"Evaluation for '{step}' in '{topic}': {student_response}"


@tool
def adjust_learning_path(current_plan: str, feedback: str, score: int) -> str:
    """
    Dynamically adjusts the learning roadmap based on performance signals.

    Args:
        current_plan: The active roadmap (text or JSON)
        feedback: Notes on student struggles or strengths
        score: Latest checkpoint score (0-100)

    Returns:
        Updated roadmap with a change log explaining what was modified and why
    """
    return f"Adjusted plan (score={score}) based on: {feedback}"
