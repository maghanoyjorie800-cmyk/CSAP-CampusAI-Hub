from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from predictive_model import predict_student, cohort_summary, intervention_for
from generative_ai import generate_answer, generate_study_plan, generate_intervention_message
from datetime import datetime

app = Flask(__name__)
app.secret_key = "campusai-capstone-demo-secret"

SCHOOL = {
    "name": "Colegio de San Antonio de Padua",
    "short": "CSAP",
    "location": "Guinsay, Danao City, Philippines",
    "founded": "2004",
}

STUDENTS = [
    {"id": 1, "name": "Alex Santos", "course": "BS Information Technology", "year": "2nd Year", "attendance": 94, "study": 9, "assignments": 91, "quiz": 88, "previous": 90},
    {"id": 2, "name": "Maria Reyes", "course": "BS Computer Science", "year": "1st Year", "attendance": 86, "study": 6, "assignments": 82, "quiz": 79, "previous": 84},
    {"id": 3, "name": "Joshua Cruz", "course": "BS Information Systems", "year": "3rd Year", "attendance": 91, "study": 8, "assignments": 87, "quiz": 85, "previous": 88},
    {"id": 4, "name": "Sofia Garcia", "course": "BS Information Technology", "year": "2nd Year", "attendance": 78, "study": 4, "assignments": 73, "quiz": 70, "previous": 76},
    {"id": 5, "name": "Daniel Lim", "course": "BS Information Systems", "year": "1st Year", "attendance": 82, "study": 5, "assignments": 77, "quiz": 74, "previous": 79},
    {"id": 6, "name": "Andrea Ramos", "course": "BS Computer Science", "year": "3rd Year", "attendance": 96, "study": 10, "assignments": 94, "quiz": 92, "previous": 91},
]

prediction_runs = []


def logged_in():
    return bool(session.get("user"))


@app.route("/")
def index():
    return redirect(url_for("dashboard") if logged_in() else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        if (username, password) == ("teacher", "teacher123"):
            session["user"] = {"name": "Teacher Admin", "role": "teacher"}
            return redirect(url_for("dashboard"))
        if (username, password) == ("student", "student123"):
            session["user"] = {"name": "Alex Santos", "role": "student"}
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid demo credentials.")
    return render_template("login.html", school=SCHOOL)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"], school=SCHOOL)


@app.route("/api/overview")
def overview():
    results = [predict_student(s) for s in STUDENTS]
    return jsonify({
        "students": len(STUDENTS),
        "predictions": len(prediction_runs),
        "average": round(sum(x["score"] for x in results) / len(results), 1),
        "at_risk": sum(x["risk"] in ("High", "Critical") for x in results),
        "watch": sum(x["risk"] == "Moderate" for x in results),
        "strong": sum(x["risk"] == "Low" for x in results),
        "summary": cohort_summary(STUDENTS),
    })


@app.route("/api/students")
def students():
    return jsonify([{**s, "prediction": predict_student(s)} for s in STUDENTS])


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    result = predict_student(data)
    prediction_runs.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "student_id": data.get("id"),
        "score": result["score"],
        "risk": result["risk"],
    })
    return jsonify(result)


@app.route("/api/intervention", methods=["POST"])
def intervention():
    data = request.get_json(force=True)
    return jsonify(intervention_for(data))


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    student = data.get("student")
    return jsonify({
        "answer": generate_answer(data.get("message", ""), student)
    })


@app.route("/api/study-plan", methods=["POST"])
def study_plan():
    data = request.get_json(force=True)
    return jsonify({
        "plan": generate_study_plan(data.get("topic", ""), data.get("hours", 6))
    })


@app.route("/api/intervention-message", methods=["POST"])
def intervention_message():
    data = request.get_json(force=True)
    return jsonify({"message": generate_intervention_message(data)})


@app.route("/api/record", methods=["POST"])
def record():
    if session.get("user", {}).get("role") != "teacher":
        return jsonify({"error": "Teacher access required"}), 403
    data = request.get_json(force=True)
    try:
        sid = int(data["id"])
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid student ID"}), 400
    student = next((x for x in STUDENTS if x["id"] == sid), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    for key in ["attendance", "study", "assignments", "quiz", "previous"]:
        if key in data:
            student[key] = float(data[key])
    return jsonify({"success": True, "student": {**student, "prediction": predict_student(student)}})


if __name__ == "__main__":
    app.run(debug=True)
