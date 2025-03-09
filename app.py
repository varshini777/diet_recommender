from flask import Flask, render_template, request
import google.generativeai as genai
import os


app = Flask(__name__)


os.environ["GOOGLE_API_KEY"] = "AIzaSyAxRo7SkwliOmPqlLXlIlmrC0XxgP3zUes"  
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")


def generate_recommendations(problem, age, dietary_preferences, Medication):
    prompt = f"""
    You are a healthcare expert. A user has reported the following:
    - Health problem: {problem}
    - Age: {age}
    - Dietary preferences: {dietary_preferences}
    - Medication: {Medication}

    Provide a personalized healthcare recommendation in the following format:
    1. **Medicine**: Suggest over-the-counter or general medicine (if applicable) and note that a doctor should be consulted for prescriptions.
    2. **Diet Recommendations**: List 3 specific diet tips or foods.
    3. **Food Suggestions**: List 3 specific meal ideas.
    4. **Workout Recommendations**: List 3 workout suggestions suited to the user's condition and age.

    Keep it concise, safe, and practical. Avoid prescribing specific dosages or controlled medications.
    """

    response = model.generate_content(prompt)
    return response.text if response else "Unable to generate recommendations."


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    if request.method == 'POST':
        problem = request.form['problem']
        age = request.form['age']
        dietary_preferences = request.form['dietary_preferences']
        Medication = request.form['Medication']

      
        recommendations = generate_recommendations(problem, age, dietary_preferences, Medication)

       
        rec_dict = {
            "medicine": "",
            "diet": [],
            "food": [],
            "workout": []
        }

        lines = recommendations.splitlines()
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("1. **Medicine**:"):
                rec_dict["medicine"] = line.replace("1. **Medicine**: ", "")
                current_section = None
            elif line.startswith("2. **Diet Recommendations**:"):
                current_section = "diet"
            elif line.startswith("3. **Food Suggestions**:"):
                current_section = "food"
            elif line.startswith("4. **Workout Recommendations**:"):
                current_section = "workout"
            elif line and current_section and not line.startswith("**"):
                rec_dict[current_section].append(line)

        return render_template('result.html', recommendations=rec_dict, problem=problem)

if __name__ == "__main__":
    app.run(debug=True, port=5000)