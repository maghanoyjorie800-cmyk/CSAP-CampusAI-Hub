# CampusAI Hub — CSAP PRO

A polished academic intelligence capstone for Colegio de San Antonio de Padua.

## System modules
1. Dashboard — cohort overview, AI workflow, early-warning distribution, quick actions.
2. Student Intelligence — searchable student profiles with prediction details.
3. Predictive Analytics — explainable weighted academic-performance model.
4. Generative Assistant — academic chat, study-plan generation, and intervention-message drafting.
5. Academic Records — teacher-only editing of demonstration academic indicators.
6. About CampusAI — presentation-ready explanation of the capstone.

## AI story for the teacher
Predictive AI estimates an academic outlook from existing indicators.
Generative AI creates useful new content from those insights.
The teacher remains in the decision loop.

## Run
```powershell
py -m pip install -r requirements.txt
py app.py
```

Open:
http://127.0.0.1:5000

Teacher demo:
teacher / teacher123

Student demo:
student / student123

## Important
This package contains an explainable Predictive AI demonstration and an offline Generative AI demonstration. For production use, connect the Generative AI layer to an approved LLM service, keep API keys server-side, add a real database, and implement proper authentication/authorization.
