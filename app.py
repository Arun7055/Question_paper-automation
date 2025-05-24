from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
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

    print("\n=== Sending request to OpenRouter ===")
    print("Payload:", payload)
    print("Headers:", headers)

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
    print("Response status code:", response.status_code)

    try:
        result = response.json()
        print("Parsed JSON response:", result)
    except Exception:
        print("❌ Failed to parse JSON. Raw response text:\n", response.text)
        raise

    if "choices" not in result:
        print("❌ API returned unexpected format:", result)
        raise Exception("LLM API failed: 'choices' missing")

    reply = result["choices"][0]["message"]["content"]
    edited_question, edited_solution = reply.split("Solution:", 1)
    return edited_question.strip(), edited_solution.strip()

@app.route('/edit-text', methods=['POST'])
def edit_text():
    data = request.json
    question = data.get('question', '')
    solution = data.get('solution', '')

    try:
        edited_q, edited_s = ask_llm(question, solution)
        return jsonify({'edited_question': edited_q, 'edited_solution': edited_s})
    except Exception as e:
        print("❌ Error in edit_text:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
