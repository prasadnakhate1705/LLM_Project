import os
import openai
import json

# Configure API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_interview_questions(
    job_description: str = "",
    resume_text: str = "",
    prompt_type: str = "technical",
    num_questions: int = 5
) -> list:
    """
    Generate a list of interview questions based on type:
      - technical: draws on the job_description
      - behavioral: draws on the job_description for culture/fit
      - resume: draws on the candidate's resume_text

    Returns:
        list: A list of question strings.

    Raises:
        ValueError: If prompt_type is invalid.
        Exception: On API errors or JSON parsing failures.
    """
    prompt_type = prompt_type.lower()
    if prompt_type == "technical":
        base_label = "Job Description"
        base_text = job_description
        role = "expert technical recruiter"
        focus = "technical questions that drill into the required skills and experience"
    elif prompt_type == "behavioral":
        base_label = "Job Description"
        base_text = job_description
        role = "expert behavioral interviewer"
        focus = "behavioral questions to assess soft‑skills, culture and fit"
    elif prompt_type == "resume":
        base_label = "Resume"
        base_text = resume_text
        role = "expert interviewer reviewing candidate resumes"
        focus = "questions that probe the candidate’s past experiences and achievements"
    else:
        raise ValueError("Invalid prompt_type: must be 'technical', 'behavioral', or 'resume'")

    prompt = (
        f"Based on the following {base_label}, generate {num_questions} concise interview questions "
        f"{focus}. Reply with a JSON array of question strings and nothing else.\n\n"
        f"{base_label}:\n{base_text}\n\nQuestions:"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an {role}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )

        content = response.choices[0].message.content.strip()
        questions = json.loads(content)
        if not isinstance(questions, list):
            raise ValueError("Expected a JSON array of questions.")
        return questions

    except Exception as e:
        raise Exception(f"Error generating interview questions ({prompt_type}): {e}")

def evaluate_answer(answer_text: str, question_text: str) -> dict:
    """
    Evaluate a candidate's answer to a specific question.

    Parameters:
        answer_text (str): Transcribed answer text.
        question_text (str): The interview question.

    Returns:
        dict: Evaluation including score, strengths, improvements, and summary.

    Raises:
        Exception: On API errors or parsing failures.
    """
    # Construct evaluative prompt that asks for JSON output
    prompt = (
        f"Evaluate the following interview answer. Respond with valid JSON containing the keys:\n"
        f"- score (integer 1-10),\n"
        f"- strengths (list of strings),\n"
        f"- improvements (list of strings),\n"
        f"- summary (string)\n\n"
        f"Question: {question_text}\n"
        f"Answer: {answer_text}\n"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert interview coach and evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        # Parse JSON
        evaluation = json.loads(content)
        # Basic validation
        required_keys = {"score", "strengths", "improvements", "summary"}
        if not required_keys.issubset(evaluation.keys()):
            raise ValueError("Missing keys in evaluation JSON.")
        return evaluation

    except Exception as e:
        raise Exception(f"Error evaluating answer: {e}")
