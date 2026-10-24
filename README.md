# FACT CHECK ✓ with RealityLensAI — Full-stack demo

This project separates the frontend and backend:
- **Frontend:** React + Vite, colorful dark-purple/teal hero, centered title, high-contrast dark text.
- **Backend:** Python + FastAPI REST API.
- **Data:** illustrative in-memory examples only. No persistent database is connected.
- **Analysis:** keyword-based demo sentiment/aspect matching. It is not a trained ML model and does not independently verify evidence.

## Run on Windows

### Terminal 1 — backend
```powershell
cd E:\RealityLensAI_FullStack\backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```
Backend docs: http://127.0.0.1:8000/docs

### Terminal 2 — frontend
Install Node.js LTS first if `npm.cmd` is not recognized.
```powershell
cd E:\RealityLensAI_FullStack\frontend
npm.cmd install
npm.cmd run dev
```
Open the Vite URL shown in the terminal, usually http://localhost:5173.

If you extract the folder somewhere else, change the `cd` paths accordingly. Keep both terminals running while testing.

## API endpoints
- `GET /` health/info
- `GET /api/platforms` catalogue
- `GET /api/platforms/{name}` platform report
- `POST /api/analyze` analyze custom review text
- `POST /api/check-claim` returns an unverified claim status and recommended checks
- `GET /api/compare` demo comparison scores

## Important
Sample review text is synthetic and only demonstrates the UI and workflow. No real review collection, external evidence verification, LLM integration, login, or database persistence is included. Before public launch, restrict CORS to your domain, add authentication/rate limits, validate privacy/legal requirements, and use a secure evidence and data storage design.
