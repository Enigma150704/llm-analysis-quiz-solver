# LLM Analysis Quiz Solver

An intelligent quiz-solving application that uses LLMs to solve data-related quizzes involving data sourcing, preparation, analysis, and visualization.

## Project Overview

This application:
- Accepts POST requests with quiz tasks
- Verifies requests using a secret key
- Renders JavaScript-rendered quiz pages using a headless browser
- Uses LLMs to solve various types of quiz questions
- Handles data sourcing, processing, analysis, and visualization tasks
- Submits answers within the required time constraints

## Features

- ✅ Secret-based authentication
- ✅ Headless browser for JavaScript-rendered pages
- ✅ LLM-powered quiz solving
- ✅ Support for multiple question types:
  - Web scraping (JavaScript-enabled)
  - API data sourcing
  - PDF and text data processing
  - Data analysis and transformations
  - Statistical/ML analysis
  - Data visualization
- ✅ Automatic retry logic for incorrect answers
- ✅ Time-limited execution (3 minutes per quiz)

## Setup

### Prerequisites

- Python 3.9+
- Node.js (for Playwright browsers)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd "LLM Analysis"
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your configuration
```

### Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
SECRET=your_secret_string
EMAIL=your_email@example.com
SYSTEM_PROMPT=Your system prompt (max 100 chars)
USER_PROMPT=Your user prompt (max 100 chars)
```

## API Endpoint

The API accepts POST requests at `/solve` with the following JSON payload:

```json
{
  "email": "your-email@example.com",
  "secret": "your-secret",
  "url": "https://example.com/quiz-834"
}
```

### Response Codes

- `200`: Valid request, quiz solving started
- `400`: Invalid JSON payload
- `403`: Invalid secret

## Running the Application

### Local Development

```bash
python app.py
```

The server will start on `http://localhost:8000`

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

## Project Structure

```
.
├── app.py                 # FastAPI application and main endpoint
├── quiz_solver.py        # Core quiz solving logic
├── llm_client.py         # LLM integration for question solving
├── browser.py            # Headless browser wrapper
├── data_processor.py     # Data processing utilities
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── LICENSE               # MIT License
└── README.md            # This file
```

## Testing

Test your endpoint with the demo quiz:

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

## License

MIT License - see LICENSE file for details

