import subprocess

question_file = "test_questions.txt"
response_file = "model_responses.txt"
api_url = "http://localhost:8080/generate"

with open(question_file, "r", encoding="utf-8") as f:
    questions = [line.strip() for line in f if line.strip()]

with open(response_file, "w", encoding="utf-8") as out_f:
    for i, question in enumerate(questions, start=1):
        print(f"Sending question {i}: {question}")
        try:
            # Format the curl command
            curl_command = [
                "curl", "-s", "-X", "POST", api_url,
                "-H", "Content-Type: application/json",
                "-d", f'{{"prompt": "{question}"}}'
            ]
            
            # Run the curl command
            result = subprocess.run(curl_command, capture_output=True, text=True)
            answer = result.stdout.strip()
        except Exception as e:
            answer = f"[ERROR] {str(e)}"
        
        out_f.write(f"Q{i}: {question}\nA{i}: {answer}\n\n")
