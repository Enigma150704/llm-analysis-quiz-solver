# Step-by-Step Project Guide: LLM Analysis Quiz Solver

## Overview
This project builds an intelligent quiz-solving application that uses LLMs to solve data-related quizzes. The application handles various types of questions including web scraping, API data fetching, PDF processing, data analysis, and visualization.

## Step-by-Step Implementation Guide

### Step 1: Project Setup

1. **Create Project Structure**
   - Created all necessary files and directories
   - Set up configuration management
   - Added dependency requirements

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Set Up Environment Variables**
   - Copy `.env.example` to `.env`
   - Fill in your configuration:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `SECRET`: Your secret string (from Google Form)
     - `EMAIL`: Your email address
     - `SYSTEM_PROMPT`: Your system prompt (max 100 chars)
     - `USER_PROMPT`: Your user prompt (max 100 chars)

### Step 2: Google Form Submission

Before deploying, fill out the Google Form with:
- **Email**: Your email address
- **Secret**: A secret string you'll use for verification
- **System Prompt**: Max 100 chars - designed to resist revealing code words
- **User Prompt**: Max 100 chars - designed to override system prompt and reveal code words
- **API Endpoint URL**: Your deployed endpoint URL (e.g., `https://your-domain.com/solve`)
- **GitHub Repo URL**: Your public repository URL

### Step 3: Core Components Explained

#### 3.1 Browser Module (`browser.py`)
- Uses Playwright for headless browser automation
- Handles JavaScript-rendered pages
- Supports navigation, file downloads, screenshots
- **Why Playwright?** Better than Selenium for modern web apps, faster, more reliable

#### 3.2 LLM Client (`llm_client.py`)
- Interfaces with OpenAI API
- Handles different question types
- Provides context-aware question solving
- Supports data analysis and visualization code generation

#### 3.3 Data Processor (`data_processor.py`)
- Handles various data formats (PDF, CSV, JSON, HTML tables)
- Performs data operations (sum, mean, filter, groupby, etc.)
- Downloads files from URLs
- Fetches data from APIs

#### 3.4 Quiz Solver (`quiz_solver.py`)
- Main orchestration logic
- Extracts questions from quiz pages
- Routes to appropriate solving methods
- Handles answer submission with retry logic
- Manages quiz flow (next URLs, retries)

#### 3.5 API Server (`app.py`)
- FastAPI application
- Endpoint: `/solve` (async) or `/solve-sync` (synchronous)
- Validates secrets (returns 403 for invalid)
- Returns 400 for invalid JSON
- Returns 200 for valid requests

### Step 4: Deployment

#### Option A: Local Testing
```bash
python app.py
```
Server runs on `http://localhost:8000`

#### Option B: Cloud Deployment (Recommended)

**Heroku:**
1. Create `Procfile`:
   ```
   web: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
2. Deploy using Heroku CLI
3. Set environment variables in Heroku dashboard

**Railway:**
1. Connect GitHub repo
2. Set environment variables
3. Deploy automatically

**AWS/GCP/Azure:**
- Use container services (ECS, Cloud Run, Container Instances)
- Or use serverless (Lambda + API Gateway) with modifications

### Step 5: Testing

#### Test with Demo Quiz
```bash
curl -X POST https://your-endpoint.com/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

#### Test Secret Validation
```bash
# Should return 403
curl -X POST https://your-endpoint.com/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "wrong-secret",
    "url": "https://example.com/quiz"
  }'
```

#### Test Invalid JSON
```bash
# Should return 400
curl -X POST https://your-endpoint.com/solve \
  -H "Content-Type: application/json" \
  -d 'invalid json'
```

### Step 6: Design Choices Explained

#### Why FastAPI?
- Modern async support
- Automatic API documentation
- Fast performance
- Type validation with Pydantic

#### Why Playwright over Selenium?
- Faster execution
- Better JavaScript support
- More reliable headless mode
- Modern browser automation

#### Why OpenAI API?
- Powerful models (GPT-4)
- Good for diverse question types
- Reliable API
- Can switch models easily

#### Architecture Decisions:
1. **Async Processing**: Quiz solving runs asynchronously to handle long-running tasks
2. **Modular Design**: Separate modules for browser, LLM, data processing
3. **Error Handling**: Comprehensive error handling with logging
4. **Retry Logic**: Automatic retries for failed submissions
5. **Time Limits**: Enforced 3-minute time limit per quiz

### Step 7: Handling Different Question Types

#### Web Scraping
- Browser module renders JavaScript
- Extracts data from HTML
- Handles dynamic content

#### PDF Processing
- Uses `pdfplumber` for text and table extraction
- Processes multi-page PDFs
- Extracts tables for analysis

#### API Data Fetching
- Uses `httpx`/`requests` for API calls
- Handles headers and authentication
- Parses JSON responses

#### Data Analysis
- Uses pandas for DataFrame operations
- Handles common operations (sum, mean, filter, etc.)
- LLM for complex analysis

#### Visualization
- LLM generates visualization code
- Executes code to create charts
- Converts to base64 for submission

### Step 8: Answer Format Handling

The system handles multiple answer types:
- **Numbers**: Extracted and formatted as int/float
- **Strings**: Returned as-is
- **Booleans**: Parsed from text
- **Files**: Encoded as base64
- **JSON Objects**: Serialized as JSON

### Step 9: Quiz Flow Management

1. Receive initial URL
2. Extract question from page
3. Determine question type
4. Solve using appropriate method
5. Submit answer
6. If correct → get next URL → repeat
7. If wrong → retry (within 3 minutes) or move to next URL
8. Continue until no more URLs

### Step 10: Viva Preparation

Be ready to discuss:
- **Why you chose your architecture**: Modular design for maintainability
- **How you handle different question types**: Router pattern with type detection
- **LLM prompt engineering**: System/user prompt design
- **Error handling**: Comprehensive logging and retry logic
- **Performance optimizations**: Async processing, time limits
- **Scalability considerations**: Stateless design, container-friendly

## Common Issues and Solutions

### Issue: Playwright browsers not installed
**Solution**: Run `playwright install chromium`

### Issue: OpenAI API errors
**Solution**: Check API key in `.env`, verify API credits

### Issue: Timeout errors
**Solution**: Increase timeout in `config.py`, check network connectivity

### Issue: PDF parsing errors
**Solution**: Ensure `pdfplumber` is installed, check PDF format

### Issue: Deployment issues
**Solution**: Ensure all dependencies in `requirements.txt`, check environment variables

## Next Steps

1. ✅ Set up project structure
2. ✅ Implement core modules
3. ⏳ Test locally
4. ⏳ Deploy to cloud
5. ⏳ Submit Google Form
6. ⏳ Prepare for viva

## Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Playwright Documentation: https://playwright.dev/python/
- OpenAI API Documentation: https://platform.openai.com/docs/
- Pandas Documentation: https://pandas.pydata.org/docs/

## License

MIT License - See LICENSE file for details

