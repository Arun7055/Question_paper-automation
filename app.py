from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import render_template
import requests

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = "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"  # Replace with your real key

def ask_llm(question, solution):
    prompt = f"""Given the following question and its solution, slightly modify the numeric values in the question (±10%) and regenerate the correct solution accordingly.

Question: {question}
Solution: {solution}
"""

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)

    try:
        result = response.json()
    except Exception:
        print("Failed to parse JSON. Raw text:", response.text)
        raise

    if "choices" not in result:
        print("API returned:", result)  # Add this
        raise Exception("LLM API failed: 'choices' missing")

    reply = result["choices"][0]["message"]["content"]
    edited_question, edited_solution = reply.split("Solution:", 1)
    return edited_question.strip(), edited_solution.strip()

@app.route('/edit-text', methods=['POST'])
def edit_text():
    data = request.json
    question = data.get('question', '')
    solution = data.get('solution', '')

    edited_q, edited_s = ask_llm(question, solution)

    return jsonify({'edited_question': edited_q, 'edited_solution': edited_s})

# @app.route('/')
# def home():
#     return "Flask backend is running!"


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
