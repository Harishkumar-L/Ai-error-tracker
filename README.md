# TraceBack AI

**From error to actionable fix.** A hackathon-ready developer productivity app that turns confusing programming errors into evidence-linked explanations, testable hypotheses, debugging steps, and GitHub-ready bug reports.

## Stack
React + Vite + JavaScript + CSS + Lucide icons, with Python + Flask + regular expressions. No database required.

## Run locally

### Flask API
```bash
cd backend
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

### React app
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open the Vite URL, usually `http://localhost:5173`. The frontend expects Flask at `http://localhost:5000`. To change it, create `frontend/.env` with `VITE_API_URL=https://your-api.example.com/api`.

## API
`POST /api/analyze` accepts `{ "language": "Python", "error": "...", "context": "..." }`. `GET /api/health` returns a health check.

## Hackathon talking points
1. Evidence-linked: extracted evidence is quoted from the actual trace, while possible causes are labeled hypotheses.
2. Beginner-friendly: the workflow explains the error before suggesting a fix.
3. Trustworthy: no guarantee claims; users get concrete checks to verify the diagnosis.
4. Practical output: a formatted Markdown issue can be copied or downloaded.

Add more patterns in `backend/analyzer.py`. For optional LLM enhancement, call your provider from Flask after deterministic extraction, pass only redacted user input, and keep deterministic evidence as the source of truth.
