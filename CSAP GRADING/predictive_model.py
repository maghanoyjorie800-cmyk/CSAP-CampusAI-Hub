def _clamp(value, low=0, high=100):
    return max(low, min(high, float(value)))


def predict_student(d):
    attendance = _clamp(d.get("attendance", 85))
    study = max(0, float(d.get("study", 6)))
    assignments = _clamp(d.get("assignments", 80))
    quiz = _clamp(d.get("quiz", 80))
    previous = _clamp(d.get("previous", 80))

    # Explainable, demonstration predictive model.
    study_score = _clamp(study * 10)
    score = (
        attendance * 0.20
        + study_score * 0.15
        + assignments * 0.20
        + quiz * 0.20
        + previous * 0.25
    )
    score = round(_clamp(score), 1)

    # Early-warning risk is based on the predicted score plus weak indicators.
    if score < 65:
        risk = "Critical"
        level = "Immediate support"
    elif score < 75:
        risk = "High"
        level = "Needs support"
    elif score < 85:
        risk = "Moderate"
        level = "Watch closely"
    else:
        risk = "Low"
        level = "Strong outlook"

    factors = []
    strengths = []
    if attendance < 85:
        factors.append({"label": "Attendance", "impact": "negative", "text": f"Attendance is {attendance:.0f}%, below the 85% reference."})
    else:
        strengths.append("Attendance is healthy.")
    if study < 5:
        factors.append({"label": "Study time", "impact": "negative", "text": f"Study time is {study:.1f} hours/week, below the 5-hour reference."})
    elif study >= 8:
        strengths.append("Study routine is consistent.")
    if assignments < 80:
        factors.append({"label": "Assignments", "impact": "negative", "text": f"Assignment performance is {assignments:.0f}% and may need attention."})
    else:
        strengths.append("Assignment completion is on track.")
    if quiz < 80:
        factors.append({"label": "Quizzes", "impact": "negative", "text": f"Quiz performance is {quiz:.0f}%, suggesting a learning gap to review."})
    else:
        strengths.append("Quiz performance is stable.")
    if previous < 80:
        factors.append({"label": "Previous grade", "impact": "negative", "text": f"Previous grade is {previous:.0f}%, so early support is recommended."})
    else:
        strengths.append("Previous performance provides a positive baseline.")

    if not factors:
        factors.append({"label": "Overall", "impact": "positive", "text": "Current indicators are consistently positive."})

    confidence = round(min(96, max(72, 72 + sum([
        attendance >= 70,
        assignments >= 65,
        quiz >= 65,
        previous >= 65,
        study >= 3,
    ]) * 4.5)), 1)

    return {
        "score": score,
        "risk": risk,
        "level": level,
        "confidence": confidence,
        "factors": factors,
        "strengths": strengths,
        "weights": [
            {"name": "Previous grade", "value": 25},
            {"name": "Attendance", "value": 20},
            {"name": "Assignments", "value": 20},
            {"name": "Quizzes", "value": 20},
            {"name": "Study time", "value": 15},
        ],
        "recommendation": intervention_for({
            "attendance": attendance,
            "study": study,
            "assignments": assignments,
            "quiz": quiz,
            "previous": previous,
            "name": d.get("name", "the student"),
        }),
        "disclaimer": "Demonstration model for academic decision support; it should not be used as the sole basis for high-stakes decisions.",
    }


def intervention_for(d):
    attendance = float(d.get("attendance", 85))
    study = float(d.get("study", 6))
    assignments = float(d.get("assignments", 80))
    quiz = float(d.get("quiz", 80))
    actions = []

    if attendance < 85:
        actions.append("Schedule an attendance check-in and identify barriers to class participation.")
    if study < 5:
        actions.append("Create a realistic weekly study schedule with short, focused sessions.")
    if assignments < 80:
        actions.append("Break upcoming assignments into smaller milestones and set a review date.")
    if quiz < 80:
        actions.append("Use retrieval practice and review the topics missed on recent quizzes.")
    if not actions:
        actions.append("Maintain the current routine and use extension activities to deepen learning.")

    return {
        "priority": "High" if len(actions) >= 3 else "Medium" if len(actions) == 2 else "Low",
        "actions": actions,
        "next_review": "Within 7 days" if len(actions) >= 2 else "Within 14 days",
    }


def cohort_summary(students):
    results = [predict_student(s) for s in students]
    return {
        "risk_labels": [
            {"label": "Low", "count": sum(r["risk"] == "Low" for r in results)},
            {"label": "Moderate", "count": sum(r["risk"] == "Moderate" for r in results)},
            {"label": "High", "count": sum(r["risk"] == "High" for r in results)},
            {"label": "Critical", "count": sum(r["risk"] == "Critical" for r in results)},
        ]
    }
