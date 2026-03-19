# StudyFlow AI Upgrade Script (Gemini Free Tier)
# Run this script from your project root: C:\Users\Tayeb\Documents\studyflow

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  StudyFlow AI Features Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# 2. Install required packages
Write-Host "Installing required packages..." -ForegroundColor Yellow
pip install google-generativeai PyPDF2

# 3. Get Gemini API Key
$envFile = ".env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    if ($envContent -match "GEMINI_API_KEY=") {
        Write-Host "GEMINI_API_KEY already exists in .env" -ForegroundColor Green
    } else {
        $apiKey = Read-Host "Enter your Google Gemini API Key (get from https://makersuite.google.com/app/apikey)"
        Add-Content $envFile "`nGEMINI_API_KEY=$apiKey"
        Write-Host "API key added to .env" -ForegroundColor Green
    }
} else {
    $apiKey = Read-Host "Enter your Google Gemini API Key (get from https://makersuite.google.com/app/apikey)"
    @"
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://studyflow_user:strongpassword@localhost/studyflow
GEMINI_API_KEY=$apiKey
"@ | Set-Content $envFile
    Write-Host ".env file created with API key" -ForegroundColor Green
}

# 4. Create ai_service.py
Write-Host "Creating ai_service.py..." -ForegroundColor Yellow
@'
import google.generativeai as genai
import os
import json
import re

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_json(text):
    """Extract JSON from Gemini response (handles markdown code blocks)."""
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        content = match.group(1)
    else:
        content = text
    try:
        return json.loads(content.strip())
    except json.JSONDecodeError:
        return {"error": "Could not parse JSON", "raw": text}

def generate_summary(text, source_lang='auto', target_lang='en'):
    """Generate a summary in target language."""
    prompt = f"""
    You are an AI study assistant. Summarize the following text (language: {source_lang}) in {target_lang}. 
    Keep the summary concise (max 200 words) and highlight key points.
    
    Text: {text}
    """
    response = model.generate_content(prompt)
    return response.text

def generate_flashcards(text, source_lang='auto', count=10):
    """Generate flashcards (front/back) for study."""
    prompt = f"""
    Extract important concepts, terms, or questions from the following text. 
    For each, create a flashcard with:
    - front: A question or term (in the original language, unless specified)
    - back: The answer or definition (in English, unless specified)
    Return a JSON array of objects with keys: "front", "back".
    Limit to {count} items.
    
    Text: {text}
    """
    response = model.generate_content(prompt)
    return extract_json(response.text)

def generate_quiz(text, source_lang='auto', num_questions=5):
    """Generate multiple-choice quiz questions."""
    prompt = f"""
    Create {num_questions} multiple-choice questions based on the following text. 
    Return a JSON array with objects containing:
    - "question": the question (in English)
    - "options": array of 4 possible answers
    - "correct": the correct answer (must match one of the options)
    - "explanation": brief explanation
    
    Text: {text}
    """
    response = model.generate_content(prompt)
    return extract_json(response.text)
'@ | Set-Content -Path ai_service.py -Encoding UTF8
Write-Host "ai_service.py created." -ForegroundColor Green

# 5. Update models.py (append Generation class)
Write-Host "Updating models.py..." -ForegroundColor Yellow
$modelsFile = "models.py"
if (Test-Path $modelsFile) {
    Add-Content $modelsFile @"

class Generation(db.Model):
    __tablename__ = 'generations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tool_type = db.Column(db.Enum('summary', 'flashcard', 'quiz'), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    output_content = db.Column(db.JSON, nullable=False)
    source_language = db.Column(db.String(10), default='auto')
    target_language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
"@
    Write-Host "Generation class appended to models.py." -ForegroundColor Green
} else {
    Write-Host "models.py not found. Please ensure you are in the correct directory." -ForegroundColor Red
    exit
}

# 6. Create templates folder if not exists
$templatesDir = "templates"
if (-Not (Test-Path $templatesDir)) {
    New-Item -ItemType Directory -Path $templatesDir
}

# 7. Create study_tools.html
Write-Host "Creating study_tools.html..." -ForegroundColor Yellow
@'
{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <h2 class="mb-4">AI Study Tools</h2>
        <ul class="nav nav-tabs mb-3" id="toolTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="summary-tab" data-bs-toggle="tab" data-bs-target="#summary" type="button" role="tab">📝 Summarize</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="flashcard-tab" data-bs-toggle="tab" data-bs-target="#flashcard" type="button" role="tab">🃏 Flashcards</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="quiz-tab" data-bs-toggle="tab" data-bs-target="#quiz" type="button" role="tab">❓ Quiz</button>
            </li>
        </ul>
        
        <div class="tab-content" id="toolTabsContent">
            <!-- Summary Tab -->
            <div class="tab-pane fade show active" id="summary" role="tabpanel">
                <form method="POST" action="{{ url_for('process_text') }}" enctype="multipart/form-data">
                    <input type="hidden" name="tool_type" value="summary">
                    <div class="mb-3">
                        <label for="text_summary" class="form-label">Paste your text or upload a PDF</label>
                        <textarea class="form-control" id="text_summary" name="text" rows="6" placeholder="Paste article, notes, or study material..."></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="pdf_summary" class="form-label">Or upload PDF</label>
                        <input class="form-control" type="file" name="pdf_file" accept=".pdf">
                    </div>
                    <div class="row mb-3">
                        <div class="col">
                            <label for="source_lang_summary" class="form-label">Source language (optional)</label>
                            <input type="text" class="form-control" name="source_lang" placeholder="e.g., fr, ar, auto">
                        </div>
                        <div class="col">
                            <label for="target_lang_summary" class="form-label">Target language</label>
                            <input type="text" class="form-control" name="target_lang" value="en" placeholder="e.g., en, fr, ar">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Generate Summary</button>
                </form>
            </div>
            
            <!-- Flashcard Tab -->
            <div class="tab-pane fade" id="flashcard" role="tabpanel">
                <form method="POST" action="{{ url_for('process_text') }}" enctype="multipart/form-data">
                    <input type="hidden" name="tool_type" value="flashcard">
                    <div class="mb-3">
                        <label for="text_flash" class="form-label">Paste your text or upload a PDF</label>
                        <textarea class="form-control" id="text_flash" name="text" rows="6" placeholder="Paste article, notes, or study material..."></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="pdf_flash" class="form-label">Or upload PDF</label>
                        <input class="form-control" type="file" name="pdf_file" accept=".pdf">
                    </div>
                    <div class="row mb-3">
                        <div class="col">
                            <label for="source_lang_flash" class="form-label">Source language (optional)</label>
                            <input type="text" class="form-control" name="source_lang" placeholder="auto">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Generate Flashcards</button>
                </form>
            </div>
            
            <!-- Quiz Tab -->
            <div class="tab-pane fade" id="quiz" role="tabpanel">
                <form method="POST" action="{{ url_for('process_text') }}" enctype="multipart/form-data">
                    <input type="hidden" name="tool_type" value="quiz">
                    <div class="mb-3">
                        <label for="text_quiz" class="form-label">Paste your text or upload a PDF</label>
                        <textarea class="form-control" id="text_quiz" name="text" rows="6" placeholder="Paste article, notes, or study material..."></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="pdf_quiz" class="form-label">Or upload PDF</label>
                        <input class="form-control" type="file" name="pdf_file" accept=".pdf">
                    </div>
                    <div class="row mb-3">
                        <div class="col">
                            <label for="source_lang_quiz" class="form-label">Source language (optional)</label>
                            <input type="text" class="form-control" name="source_lang" placeholder="auto">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Generate Quiz</button>
                </form>
            </div>
        </div>
        
        <hr class="my-4">
        <a href="{{ url_for('history') }}" class="btn btn-outline-secondary">View My History</a>
    </div>
</div>
{% endblock %}
'@ | Set-Content -Path "$templatesDir\study_tools.html" -Encoding UTF8
Write-Host "study_tools.html created." -ForegroundColor Green

# 8. Create tool_result.html
Write-Host "Creating tool_result.html..." -ForegroundColor Yellow
@'
{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <h2 class="mb-4">Your {{ tool_type|capitalize }}</h2>
        
        {% if tool_type == 'summary' %}
            <div class="card">
                <div class="card-body">
                    {{ output }}
                </div>
            </div>
        {% elif tool_type == 'flashcard' %}
            {% set flashcards = output|tojson %}
            {% if flashcards.error %}
                <div class="alert alert-danger">Error: {{ flashcards.error }}</div>
                <pre>{{ flashcards.raw }}</pre>
            {% else %}
                {% for card in flashcards %}
                <div class="card mb-3">
                    <div class="card-header">{{ card.front }}</div>
                    <div class="card-body">{{ card.back }}</div>
                </div>
                {% endfor %}
                <a href="#" class="btn btn-success" onclick="exportAnki()">Export to Anki (CSV)</a>
            {% endif %}
        {% elif tool_type == 'quiz' %}
            {% set quiz = output|tojson %}
            {% if quiz.error %}
                <div class="alert alert-danger">Error: {{ quiz.error }}</div>
                <pre>{{ quiz.raw }}</pre>
            {% else %}
                {% for q in quiz %}
                <div class="card mb-3">
                    <div class="card-header">{{ loop.index }}. {{ q.question }}</div>
                    <div class="card-body">
                        <ul class="list-unstyled">
                            {% for opt in q.options %}
                            <li>{% if opt == q.correct %}✅ {% else %}○ {% endif %}{{ opt }}</li>
                            {% endfor %}
                        </ul>
                        <p class="text-muted mt-2"><strong>Explanation:</strong> {{ q.explanation }}</p>
                    </div>
                </div>
                {% endfor %}
            {% endif %}
        {% endif %}
        
        <a href="{{ url_for('study_tools') }}" class="btn btn-primary mt-3">Try Another</a>
        <a href="{{ url_for('history') }}" class="btn btn-secondary mt-3">View History</a>
    </div>
</div>

<script>
function exportAnki() {
    alert("Anki export will be implemented soon!");
}
</script>
{% endblock %}
'@ | Set-Content -Path "$templatesDir\tool_result.html" -Encoding UTF8
Write-Host "tool_result.html created." -ForegroundColor Green

# 9. Create history.html
Write-Host "Creating history.html..." -ForegroundColor Yellow
@'
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col">
        <h2 class="mb-4">My Generation History</h2>
        {% if generations %}
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Date</th>
                        <th>Preview</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for gen in generations %}
                    <tr>
                        <td>{{ gen.tool_type|capitalize }}</td>
                        <td>{{ gen.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                        <td>{{ gen.input_text[:50] }}...</td>
                        <td><a href="{{ url_for('view_generation', gen_id=gen.id) }}" class="btn btn-sm btn-info">View</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p>No generations yet. <a href="{{ url_for('study_tools') }}">Try the AI tools!</a></p>
        {% endif %}
    </div>
</div>
{% endblock %}
'@ | Set-Content -Path "$templatesDir\history.html" -Encoding UTF8
Write-Host "history.html created." -ForegroundColor Green

# 10. Database table creation instructions
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS - Manual Actions Required" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host @"

1. **Create the new database table**
   Run this SQL in your MySQL client (e.g., MySQL Workbench or command line):
   
   CREATE TABLE generations (
       id INT AUTO_INCREMENT PRIMARY KEY,
       user_id INT NOT NULL,
       tool_type ENUM('summary', 'flashcard', 'quiz') NOT NULL,
       input_text TEXT NOT NULL,
       output_content JSON NOT NULL,
       source_language VARCHAR(10) DEFAULT 'auto',
       target_language VARCHAR(10) DEFAULT 'en',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
   );

2. **Update app.py**
   Add the following imports at the top:
   
   from ai_service import generate_summary, generate_flashcards, generate_quiz
   import PyPDF2
   from models import Generation

   Then add the new routes (study_tools, process_text, history, view_generation) – 
   you can copy them from the previous message or the documentation.

3. **Add navigation link**
   In your base.html, add a new nav item for "AI Tools" pointing to {{ url_for('study_tools') }}.

4. **Restart your Flask app**
   Run: python run.py
"@ -ForegroundColor Yellow

Write-Host "`nSetup complete! After following the manual steps, your StudyFlow will have AI-powered study tools." -ForegroundColor Green