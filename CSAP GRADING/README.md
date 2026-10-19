# CampusAI Hub — Predictive + Generative AI

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Run `python -m pip install -r requirements.txt`.
4. Run `python app.py`.
5. Open `http://127.0.0.1:5000` in your browser.

## Demo accounts
- Teacher Admin: `teacher` / `teacher123`
- Student: `student` / `student123`

## Account registration and approval
- Use **Create an account** on the sign-in page to request a student account.
- Newly registered accounts remain **Pending** and cannot sign in until approved.
- Sign in as the teacher admin and open **Account Approvals** in the sidebar.
- The teacher admin can view all accounts, search/filter by status, approve pending requests, reject requests, and revoke access for approved student accounts.
- Account details and password hashes are stored in the local SQLite database `campusai_accounts.db`, created automatically on first run. Plain-text passwords are not stored.
- The original predictive AI, generative AI, student profiles, and academic records pages are retained.

## Before public deployment
Change `CAMPUSAI_SECRET_KEY` to a long random secret and replace the demo teacher credentials with a secure administrator account. The included demo credentials are for local testing only.
