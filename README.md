@"
# StudyFlow – Japanese Vocabulary Tracker

![Demo GIF](screenshots/demo.gif)  
*(Add a demo GIF or screenshot later)*

[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey?logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)](https://mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)](https://getbootstrap.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A full-stack web application to help learners track Japanese vocabulary by JLPT level (N5–N1). Built with Flask and MySQL, it features user authentication, a dashboard with progress charts, and a quiz mode.

---

## Why This Project?

I built StudyFlow to combine my passion for web development with my personal journey learning Japanese. As I prepare to move to Japan for work, this project demonstrates my technical skills, commitment to the language, and ability to build a complete, user-friendly application.

---

## Features

- 🔐 **User Authentication** – Register, log in, and log out securely.
- 📚 **Vocabulary Management** – Add, edit, and delete words with JLPT levels.
- 📊 **Dashboard** – Visual progress chart (Chart.js) showing words learned per level.
- ❓ **Quiz Mode** – Generate random quizzes with multiple choice and instant scoring.
- 🔍 **Filter & Search** – Filter words by JLPT level.
- 📱 **Responsive Design** – Works on desktop and mobile (Bootstrap 5).

---

## Live Demo

👉 *Coming soon – add your deployed link here*

---

## Screenshots

| Dashboard | Word List | Quiz |
|-----------|-----------|------|
| ![Dashboard](screenshots/dashboard.png) | ![Words](screenshots/words.png) | ![Quiz](screenshots/quiz.png) |

*(Replace with your actual screenshots)*

---

## Technologies Used

- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: MySQL (with PyMySQL)
- **Frontend**: HTML, CSS, Bootstrap 5, Chart.js, JavaScript
- **Environment**: python-dotenv

---

## Setup & Installation

### Prerequisites
- Python 3.8+, MySQL, Git

### 1. Clone the repository
```bash
git clone https://github.com/tayebmekati37-art/studyflow.git
cd studyflow
