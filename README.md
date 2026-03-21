# StudyFlow – Japanese Vocabulary Tracker

[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey?logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)](https://mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)](https://getbootstrap.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A full‑stack web app to track Japanese vocabulary by JLPT level (N5–N1).  
Built with Flask and MySQL, it includes user authentication, a dashboard with charts, a quiz, and AI study tools.

![Screenshot placeholder](screenshots/dashboard.png)

---

## Features

- 🔐 **User Authentication** – Register, log in, and track progress.
- 📚 **Vocabulary Management** – Add, edit, and delete words with reading, meaning, and JLPT level.
- 📊 **Dashboard** – See a bar chart of learned words per level and a line chart of daily additions.
- ❓ **Quiz Mode** – 10 random multiple‑choice questions with instant scoring.
- 🔍 **Filter & Search** – Filter words by JLPT level.
- 🤖 **AI Tools** – Summarize text, generate flashcards, and create quizzes using Google Gemini.
- 🌓 **Dark Mode** – Toggle between light and dark themes (persisted via localStorage).
- 📥 **CSV Export** – Download your entire vocabulary as a CSV file.
- 🔥 **Daily Streak** – Tracks consecutive login days.

---

## Tech Stack

- **Backend**: Python, Flask, Flask‑SQLAlchemy, Flask‑Login, Flask‑WTF
- **Database**: MySQL (PyMySQL driver)
- **Frontend**: HTML, CSS, Bootstrap 5, Chart.js
- **AI**: Google Gemini API (`gemini-pro`)
- **Environment**: python‑dotenv

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL server
- Git

### Clone and Install
```bash
git clone https://github.com/tayebmekati37-art/studyflow.git
cd studyflow
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
