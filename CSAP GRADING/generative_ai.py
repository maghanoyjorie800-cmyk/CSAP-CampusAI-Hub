def _name(student):
    return (student or {}).get("name", "there")


def generate_answer(q, student=None):
    raw = (q or "").strip()
    text = raw.lower()
    name = _name(student)

    if not text:
        return "Ask me about Predictive AI, Generative AI, student support, study strategies, or how this CampusAI Hub works."

    if "predictive" in text or "prediction" in text:
        return (
            "Predictive AI analyzes existing academic indicators to estimate a future outcome. "
            "In this capstone, the model uses attendance, study time, assignments, quizzes, and previous grades. "
            "The result includes a predicted score, risk level, confidence indicator, influential factors, and recommended intervention."
        )
    if "generative" in text or "generation" in text:
        return (
            "Generative AI creates new responses or plans from a user's prompt. "
            "CampusAI demonstrates this through its academic assistant, personalized study-plan generator, "
            "and intervention-message generator. In a production system, this layer could be connected to an approved LLM API."
        )
    if "how" in text and ("system" in text or "work" in text or "campusai" in text):
        return (
            "CampusAI follows a four-stage workflow: collect academic indicators, predict a performance outlook, "
            "generate personalized support, and keep a teacher in the decision loop. "
            "The Predictive AI is the scoring/early-warning layer, while the Generative AI turns insights into useful explanations and plans."
        )
    if "risk" in text or "at risk" in text or "danger" in text:
        if student:
            return (
                f"For {name}, the current model risk is {student.get('prediction', {}).get('risk', 'not calculated')}. "
                "Risk is an early-warning signal, not a diagnosis. Review the contributing indicators and confirm the situation with the student."
            )
        return "Risk levels are used as early-warning signals. They should trigger human review and support, not automatic punishment or high-stakes decisions."
    if "study" in text or "exam" in text or "review" in text:
        return (
            "Try a focused cycle: 30–40 minutes of active practice, a short break, then self-test without notes. "
            "Prioritize the topics you cannot explain clearly and finish with a quick error review."
        )
    if "flask" in text or "python" in text:
        return (
            "This project uses Python and Flask for the web application. "
            "The predictive_model.py module contains the explainable prediction logic, while generative_ai.py contains the "
            "Generative AI demonstration layer."
        )
    if "teacher" in text or "intervention" in text:
        return (
            "Teachers can update academic records, run predictions, review risk factors, and generate a suggested intervention. "
            "The design keeps a human decision-maker in the loop."
        )
    if "hello" in text or text in {"hi", "hey"}:
        return f"Hello, {name}! I'm CampusAI. I can explain the AI features, analyze an academic profile, or build a study plan."

    return (
        "I can help with this capstone's Predictive AI, Generative AI, academic risk signals, "
        "study planning, Python/Flask, or student-support workflows. Try asking me to explain a specific feature."
    )


def generate_study_plan(topic, hours):
    topic = (topic or "your topic").strip()
    try:
        hours = max(1, int(float(hours)))
    except (TypeError, ValueError):
        hours = 6

    sessions = max(3, min(7, hours))
    focus = [
        f"Learn the core concepts of {topic}.",
        f"Work through examples and guided exercises for {topic}.",
        f"Practice {topic} without notes and identify weak areas.",
        f"Complete a mini-project, case study, or practice test on {topic}.",
        f"Review mistakes and create a one-page summary of {topic}.",
        f"Teach the key ideas of {topic} aloud or to a study partner.",
        f"Take a final self-test and schedule the next review.",
    ]
    return [
        {
            "day": i + 1,
            "duration": max(25, round((hours * 60) / sessions)),
            "task": focus[i],
        }
        for i in range(sessions)
    ]


def generate_intervention_message(data):
    name = (data.get("name") or "Student").strip()
    risk = data.get("risk", "Moderate")
    actions = data.get("actions", [])
    opening = {
        "Critical": f"Hi {name}, we noticed a few academic indicators that may benefit from prompt support.",
        "High": f"Hi {name}, we'd like to check in and help you strengthen a few academic areas.",
        "Moderate": f"Hi {name}, you're making progress, and we'd like to help you strengthen a few areas before they become bigger challenges.",
        "Low": f"Hi {name}, your current indicators are encouraging. Let's keep the momentum going.",
    }.get(risk, f"Hi {name}, we'd like to support your academic progress.")

    if actions:
        body = "Suggested next steps: " + " ".join(actions)
    else:
        body = "Let's review your current routine and agree on one practical next step."
    return f"{opening} {body} Your teacher or adviser can help adjust the plan based on your actual circumstances."
