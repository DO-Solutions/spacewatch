# SpaceWatch 🚀

AI-powered monitoring for DigitalOcean Spaces with natural language queries, real-time metrics, and access log analysis.

## Features

- **AI Chat Interface**: Query storage using natural language ("Show me the largest files", "Which IP uploaded file.pdf?")
- **Metrics Dashboard**: Track storage size, requests, bandwidth, and errors over time
- **Access Log Analysis**: Parse S3 logs to find upload IPs, audit object access, and track events
- **Storage Alerts**: Browser notifications when thresholds are reached
- **Automatic Snapshots**: Optional scheduler to capture metrics every 5 minutes

## Quick Start

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure environment** (copy `sample.env` to `.env`)
```bash
# DigitalOcean Spaces
SPACES_REGION=sgp1
SPACES_ENDPOINT=https://sgp1.digitaloceanspaces.com
SPACES_KEY=your_access_key
SPACES_SECRET=your_secret_key

# AI Agent (OpenAI-compatible)
DO_AGENT_URL=https://api.openai.com/v1/chat/completions
DO_AGENT_KEY=your_api_key

# Optional: Access Logs
ACCESS_LOGS_BUCKET=my-logs
ACCESS_LOGS_ROOT_PREFIX=spaces-logs/
```

3. **Run the application**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Access the dashboard at `http://localhost:8000`

## Usage

### Chat Examples
- "List objects in my-bucket"
- "Show me the largest files in prod-assets"
- "What's the most recently uploaded file?"
- "Which IP uploaded myfile.pdf?"

### Key API Endpoints
- `POST /chat` - AI assistant
- `GET /metrics/series?source_bucket=X&hours=24` - Metrics time series
- `GET /tools/storage-summary?bucket=X` - Storage stats
- `GET /health` - System status

## Configuration

### Required Variables
- `SPACES_REGION`, `SPACES_ENDPOINT`, `SPACES_KEY`, `SPACES_SECRET` - DigitalOcean Spaces credentials
- `DO_AGENT_URL`, `DO_AGENT_KEY` - OpenAI-compatible API endpoint

### Optional Variables
- `ACCESS_LOGS_BUCKET` - Bucket containing S3 access logs
- `METRICS_BUCKET` - Where to store metrics snapshots (defaults to ACCESS_LOGS_BUCKET)
- `APP_API_KEY` - Protect endpoints with X-API-Key header
- `ENABLE_SCHEDULER=true` - Auto-capture metrics every 5 minutes
- `FALLBACK_BUCKETS=bucket1,bucket2` - If list_buckets permission unavailable

See `sample.env` for all options.

## Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
COPY static/ static/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t spacewatch .
docker run -p 8000:8000 --env-file .env spacewatch
```

## License

Open source - check with repository owner for details.
