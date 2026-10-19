def predict_student(d):
    attendance=float(d.get("attendance",85)); study=float(d.get("study",6)); assignments=float(d.get("assignments",80)); quiz=float(d.get("quiz",80)); previous=float(d.get("previous",80))
    score=max(0,min(100,attendance*.20+min(study*10,100)*.15+assignments*.20+quiz*.20+previous*.25))
    level="Strong outlook" if score>=85 else "Moderate outlook" if score>=75 else "Needs support"
    factors=[]
    if attendance<85:factors.append("Attendance is below the 85% reference level.")
    if study<5:factors.append("Study time is relatively low.")
    if assignments<80:factors.append("Assignment performance could improve.")
    if quiz<80:factors.append("Quiz performance could improve.")
    if not factors:factors.append("Current indicators are consistently positive.")
    return {"score":round(score,1),"level":level,"factors":factors}
