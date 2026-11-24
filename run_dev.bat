@echo off
start "BrandPulse Backend" cmd /k "cd backend && if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) && uvicorn app.main:app --reload --port 8000"
start "BrandPulse Frontend" cmd /k "cd frontend && npm run dev"
