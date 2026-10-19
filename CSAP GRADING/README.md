# CampusAI Hub — CSAP

CampusAI Hub is a Flask-based student success demo for Colegio de San Antonio de Padua (CSAP), with account registration and teacher-admin approval, student profiles, academic records, predictive analysis, and a generative AI study assistant.

## Run locally

```bash
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Demo logins

- Teacher admin: `teacher` / `teacher123`
- Demo student: `student` / `student123`

Change the demo passwords and set `CAMPUSAI_SECRET_KEY` to a strong random value before public deployment.

## Account and academic-record behavior

- Newly registered accounts are students and remain pending until approved by the teacher admin.
- Only approved student accounts can sign in and are included in the teacher's student list and Academic Records selector.
- Registered students' attendance, study hours, assignment score, quiz score, and previous grade are stored in SQLite and reused by the student profile and predictive feature.
- The teacher admin can see all accounts and approve or reject/revoke access.
- Student sessions can only request their own registered student profile; teacher-only account management and academic-record writes are protected on the server.

## Deployment note

The default SQLite database is created beside `app.py`. On hosting platforms with an ephemeral filesystem, configure a persistent disk or migrate to a managed database before relying on saved account/academic data across redeployments. Do not commit the generated `campusai_accounts.db` file to a public repository.
