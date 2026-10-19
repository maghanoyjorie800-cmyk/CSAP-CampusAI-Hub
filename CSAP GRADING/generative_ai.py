def generate_answer(q):
    q=q.lower().strip()
    if not q:return "Ask me about CampusAI Hub, Predictive AI, Generative AI, programming, or study strategies."
    if "predictive" in q:return "Predictive AI uses data to estimate an outcome. CampusAI combines attendance, study time, assignments, quizzes and previous grades to produce an academic performance estimate."
    if "generative" in q:return "Generative AI creates new content from prompts. CampusAI uses it for the academic assistant and study-plan generator."
    if "system" in q or "campusai" in q:return "CampusAI Hub is a school-focused platform with two AI layers: Predictive AI for academic estimates and Generative AI for explanations, questions and study plans."
    if "python" in q:return "Python is a general-purpose programming language. This project uses Flask for the web app and Python modules for the AI features."
    if "study" in q or "exam" in q:return "Try 25–40 minutes of focused study, a short break, then self-test without notes. Prioritize topics you cannot explain clearly."
    if "hello" in q or "hi" in q:return "Hello! I'm CampusAI. Ask me about this system, AI, programming or studying."
    return "I can help with CampusAI Hub, Predictive AI, Generative AI, programming basics, school projects and study strategies. Try a specific question."

def generate_study_plan(topic,hours):
    try:h=max(1,int(hours))
    except:h=6
    mins=max(30,round(h*60/5)); topic=topic or "your topic"
    return [f"Session {i} ({mins} min): "+x for i,x in enumerate([f"Learn the core concepts of {topic}.","Work through examples and guided exercises.","Practice without notes and identify weak areas.","Complete a mini-project or practice test.","Review mistakes and create a one-page summary."],1)]
