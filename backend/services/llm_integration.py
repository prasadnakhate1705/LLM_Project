import os
import openai
import json

# Configure API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_interview_questions(job_description: str, num_questions: int = 5) -> list:
    """
    Generate a list of interview questions based on the job description.

    Parameters:
        job_description (str): Full job description text.
        num_questions (int): Number of questions to generate.

    Returns:
        list: A list of question strings.

    Raises:
        Exception: On API errors or parsing failures.
    """
    prompt = (
        f"Based on the following job description, generate {num_questions} concise interview questions "
        "that assess a candidate's skills, experience, and cultural fit. "
        "Respond with a JSON array of question strings and nothing else.\n\n"
        f"Job Description:\n{job_description}\n\nQuestions:"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert technical recruiter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )

        content = response.choices[0].message.content.strip()
        # Parse JSON array
        questions = json.loads(content)
        if not isinstance(questions, list):
            raise ValueError("Expected a JSON array of questions.")
        return questions

    except Exception as e:
        raise Exception(f"Error generating interview questions: {e}")


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
