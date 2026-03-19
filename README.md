
StudyFlow – Japanese Vocabulary Tracker

[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey?logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)](https://mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)](https://getbootstrap.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A web app to track Japanese vocabulary by JLPT level (N5–N1).  
Built with Flask and MySQL, it includes user accounts, a dashboard with charts, and a quiz mode.

---

 What it does

- Register and log in
- Add, edit, or delete vocabulary words (with reading, meaning, and JLPT level)
- See your progress in a bar chart (grouped by level)
- Take a quiz: 10 random multiple-choice questions, score shown at the end
- Filter your word list by level

---
 Screenshots

| Dashboard | Word List | Quiz |
|-----------|-----------|------|
| ![](screenshots/dashboard.png) | ![](screenshots/words.png) | ![](screenshots/quiz.png) |



---

  Tech stack

- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: MySQL (PyMySQL driver)
- **Frontend**: HTML, CSS, Bootstrap 5, Chart.js
- **Environment**: python-dotenv for configuration

---

 Setup locally

 Requirements
- Python 3.8+
- MySQL server
- Git

 Steps

1. **Clone the repo**
   ```bash
   git clone https://github.com/tayebmekati37-art/studyflow.git
   cd studyflow
