\# CLAUDE.md



\## Project



This is a Streamlit planner app built with Python, Streamlit, and SQLite.



The app lets users create plans, organize tasks into buckets, manage checklist items, and view work in Board and Grid views.



\## Tech Stack



\- Python

\- Streamlit

\- SQLite

\- GitHub

\- Streamlit Community Cloud



\## Main Files



\- `app.py` - Streamlit UI

\- `database.py` - SQLite database functions

\- `planner.db` - local SQLite database

\- `requirements.txt` - dependencies

\- `README.md` - project overview



\## Current Features



\- Create/open plans

\- Rename/delete plans

\- Default buckets:

&#x20; - Backlog

&#x20; - Up next

&#x20; - In progress

&#x20; - Blocked

&#x20; - Completed

\- Add/edit/delete tasks

\- Move tasks between buckets

\- Due date

\- Priority

\- Assignee

\- Labels/tags

\- Completed flag

\- Checklist items

\- Checklist progress

\- Board view

\- Grid view

\- SQLite storage

\- Basic UI styling



\## Rules for Claude Code



\- Keep the app beginner-friendly.

\- Do not rewrite the whole app unless asked.

\- Make small safe changes.

\- Explain changed files after editing.

\- Before large changes, create a plan first.

\- Do not remove SQLite unless asked.

\- Do not add login, payments, or complex backend yet.

\- Always test with:

&#x20; `python -m py\_compile app.py database.py`

\- Run locally with:

&#x20; `python -m streamlit run app.py`



\## Known Limitation



SQLite file storage works for local development and demos, but on Streamlit Community Cloud it is not ideal for permanent production data.

