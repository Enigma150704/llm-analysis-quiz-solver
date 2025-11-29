# Quick Start Guide

## Setup in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in:

```env
OPENAI_API_KEY=sk-your-key-here
SECRET=your-secret-string
EMAIL=your-email@example.com
SYSTEM_PROMPT=Your system prompt here (max 100 chars)
USER_PROMPT=Your user prompt here (max 100 chars)
```

### 3. Run the Server

```bash
python app.py
```

Server will start on `http://localhost:8000`

### 4. Test the Endpoint

```bash
python test_endpoint.py
```

Or manually:

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

### 5. Deploy (Choose One)

#### Option A: Railway
1. Push code to GitHub
2. Connect repo to Railway
3. Add environment variables
4. Deploy

#### Option B: Heroku
1. Install Heroku CLI
2. `heroku create your-app-name`
3. `git push heroku main`
4. Set config vars in dashboard

#### Option C: Render
1. Create new Web Service
2. Connect GitHub repo
3. Add environment variables
4. Deploy

## Next Steps

- Fill out the Google Form with your details
- Test with the demo quiz URL
- Prepare for the viva!

## Troubleshooting

**Playwright error?**
```bash
playwright install chromium
```

**OpenAI API error?**
- Check your API key in `.env`
- Verify you have credits

**Port already in use?**
- Change PORT in `.env` or use: `PORT=8001 python app.py`

