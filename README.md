# BrandPulse 3D — Brand Sentiment & Reputation Monitor

Full-stack **AI-ML + Introduction to Data Analytics (IDA)** system built for **Topic 46: Brand Sentiment & Reputation Monitor** and aligned directly with **Review 2 Assessment Criteria**.

## Quick Setup (3 Parts)

### Part 1: Data Science & Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Fast 15-second setup (VADER + Contextual Bigram ML):
pip install -r requirements-lite.txt

# OR Full setup (adds HuggingFace RoBERTa + PyTorch):
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

### Part 2: Verify AI Core & Automated Tests
```bash
cd backend
pytest -v
```
Inspect live API docs at `http://localhost:8000/docs`.

### Part 3: 3D Animated React Frontend
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in Chrome.

### One-Command Dev Launcher
```bash
chmod +x run_dev.sh
./run_dev.sh
```
On Windows, run `run_dev.bat`.
