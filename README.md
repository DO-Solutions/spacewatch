# SpaceWatch 🚀

AI-driven observability backend for DigitalOcean Spaces (S3-compatible object storage) with real-time metrics, access log analysis, and intelligent querying capabilities.

## Overview

SpaceWatch provides comprehensive monitoring and analytics for your DigitalOcean Spaces buckets with an AI-powered chat interface. It automatically collects storage metrics, analyzes access logs, and allows you to query your data using natural language.

## Key Features

- **AI-Powered Chat Interface**: Ask questions in natural language about your storage ("What's the largest file in bucket X?", "Show me access logs from yesterday")
- **Real-Time Metrics Dashboard**: Track storage size, request counts, bandwidth usage, and error rates over time
- **Access Log Analysis**: Parse and search through S3 access logs with support for gzip compression
- **Storage Alerts**: Set thresholds and get browser notifications when limits are approached
- **Object Audit Trail**: Track upload/download/delete events for specific objects with IP addresses and timestamps
- **Top IPs Visualization**: Bar charts showing most active IP addresses accessing your buckets
- **Automatic Metrics Snapshots**: Optional scheduler to capture metrics every 5 minutes
- **CloudTrail-style Timeline**: View complete access history for any object

## Architecture

SpaceWatch sits between an AI agent (OpenAI-compatible API) and your DigitalOcean Spaces storage:

```
┌─────────────┐      ┌──────────────┐      ┌───────────────────┐
│   Browser   │ ───> │  SpaceWatch  │ ───> │ DigitalOcean      │
│  Dashboard  │ <─── │   Backend    │ <─── │ Spaces (S3-API)   │
└─────────────┘      └──────────────┘      └───────────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  AI Agent    │
                     │ (OpenAI API) │
                     └──────────────┘
```

The backend:
- Exposes REST API endpoints for metrics and chat
- Calls AI agent with tool schemas (buckets, logs, storage summary, etc.)
- Executes tool calls internally and returns human-readable answers
- Stores metrics snapshots as JSONL in Spaces
- Parses S3 access logs to extract request data

## Installation

### Prerequisites

- Python 3.8+
- DigitalOcean Spaces account with API keys
- OpenAI-compatible AI agent endpoint (OpenAI, Azure OpenAI, etc.)
- Optional: Access logging enabled on your Spaces buckets

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/zasghar26/spacewatch.git
cd spacewatch
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Copy the sample environment file and edit it:
```bash
cp sample.env .env
```

Edit `.env` with your credentials:
```bash
# DigitalOcean Spaces
SPACES_REGION=sgp1
SPACES_ENDPOINT=https://sgp1.digitaloceanspaces.com
SPACES_KEY=your_spaces_access_key
SPACES_SECRET=your_spaces_secret_key

# AI Agent (OpenAI-compatible)
DO_AGENT_URL=https://your-agent-host/v1/chat/completions
DO_AGENT_KEY=your_agent_api_key

# Access Logs + Metrics
ACCESS_LOGS_BUCKET=my-access-logs
ACCESS_LOGS_ROOT_PREFIX=spaces-logs/

METRICS_BUCKET=my-access-logs
METRICS_PREFIX=spacewatch-metrics/

# App Security (optional but recommended)
APP_API_KEY=your_secret_key
```

4. **Run the application**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SPACES_REGION` | DigitalOcean Spaces region | `sgp1`, `nyc3`, `sfo3` |
| `SPACES_ENDPOINT` | Spaces API endpoint URL | `https://sgp1.digitaloceanspaces.com` |
| `SPACES_KEY` | Spaces access key | Your access key |
| `SPACES_SECRET` | Spaces secret key | Your secret key |
| `DO_AGENT_URL` | OpenAI-compatible chat completions endpoint | `https://api.openai.com/v1/chat/completions` |
| `DO_AGENT_KEY` | AI agent API key | Your OpenAI API key |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ACCESS_LOGS_BUCKET` | - | Bucket containing S3 access logs |
| `ACCESS_LOGS_ROOT_PREFIX` | - | Prefix path for access logs |
| `METRICS_BUCKET` | `ACCESS_LOGS_BUCKET` | Bucket for storing metrics snapshots |
| `METRICS_PREFIX` | `spacewatch-metrics/` | Prefix for metrics storage |
| `METRICS_GZIP` | `true` | Compress metrics with gzip |
| `APP_API_KEY` | - | Protect endpoints with X-API-Key header |
| `FALLBACK_BUCKETS` | - | Comma-separated list of buckets (when list_buckets fails) |
| `SCHEDULER_SOURCE_BUCKETS` | - | Buckets to snapshot (doesn't need list_buckets permission) |
| `ENABLE_SCHEDULER` | `false` | Auto-snapshot metrics every 5 minutes |
| `SNAPSHOT_EVERY_SEC` | `300` | Snapshot interval in seconds |
| `MAX_LOG_BYTES` | `10485760` | Max bytes to read per log file (10MB) |
| `MAX_LOG_LINES` | `300` | Max lines to return when reading logs |
| `RATE_LIMIT_RPS` | `2.0` | Requests per second limit |
| `RATE_LIMIT_BURST` | `10` | Token bucket burst size |
| `AGENT_MAX_STEPS` | `8` | Max tool calls per chat request |

## Usage

### Web Dashboard

Open your browser to `http://localhost:8000` to access the interactive dashboard:

- **Metrics View**: Select a bucket to see storage, requests, errors, and bandwidth charts
- **Alerts**: Set storage thresholds and alert percentages (with browser notifications)
- **Chat Interface**: Ask questions like:
  - "List objects in my-bucket"
  - "Show me the largest files in prod-assets"
  - "What's the most recently uploaded file?"
  - "Show access logs for my-bucket from yesterday"
  - "Which IP uploaded file.pdf?"

### API Endpoints

#### Chat with AI Assistant
```bash
POST /chat
Content-Type: application/json
X-API-Key: your_api_key

{
  "message": "Show me the largest files in my-bucket"
}
```

#### Get Metrics for a Bucket
```bash
GET /metrics/series?source_bucket=my-bucket&hours=24&limit=500
X-API-Key: your_api_key
```

#### List Available Buckets
```bash
GET /tools/buckets
X-API-Key: your_api_key
```

#### Storage Summary
```bash
GET /tools/storage-summary?bucket=my-bucket&prefix=uploads/
X-API-Key: your_api_key
```

#### Top Largest Files
```bash
GET /tools/top-largest?bucket=my-bucket&limit=20
X-API-Key: your_api_key
```

#### Health Check
```bash
GET /health
```

Returns system status, configuration, and bucket cache info.

## AI Tool Framework

The AI agent has access to these tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `buckets` | List allowed Spaces buckets | - |
| `list_objects` | List objects in bucket/prefix | `bucket`, `prefix`, `max_items` |
| `recent_objects` | Most recently modified objects | `bucket`, `prefix`, `limit` |
| `storage_summary` | Total bytes/objects for bucket | `bucket`, `prefix` |
| `top_largest` | Largest objects by size | `bucket`, `prefix`, `limit` |
| `snapshot` | Write metrics snapshot | `source_bucket`, `source_prefix` |
| `metrics_sources` | Discover buckets from snapshots | `hours` |
| `metrics_series` | Get time series data | `source_bucket`, `hours`, `limit` |
| `list_access_logs` | List log files for bucket | `source_bucket`, `date_yyyy_mm_dd` |
| `read_log` | Read tail of log file | `bucket`, `key`, `tail_lines` |
| `search_logs` | Search access logs with filters | `source_bucket`, `method`, `object_key`, `status_prefix` |
| `object_audit` | Event timeline for object | `source_bucket`, `object_key`, `methods` |

## Access Log Analysis

SpaceWatch parses S3 access logs to extract:
- Request timestamps
- HTTP methods (GET, PUT, DELETE, HEAD)
- Response status codes
- IP addresses
- Bytes transferred

### Finding Upload IP Address

To find which IP uploaded a specific file:

1. Via chat: "Which IP uploaded myfile.pdf to my-bucket?"
2. Via API:
```bash
POST /chat
{
  "message": "Find the IP that uploaded myfile.pdf using object_audit"
}
```

The AI will:
1. Call `recent_objects` to find the file
2. Call `object_audit` with `methods=["PUT"]`
3. Return the IP address and timestamp

## Metrics Snapshots

Metrics are stored as JSONL (JSON Lines) files in your metrics bucket:

```
spacewatch-metrics/
  dt=2024-01-15/
    hour=10/
      metrics.jsonl.gz
    hour=11/
      metrics.jsonl.gz
```

Each line contains:
```json
{
  "ts": "2024-01-15T10:05:00.000Z",
  "source_bucket": "my-bucket",
  "source_objects": 1250,
  "source_bytes": 52428800,
  "requests_total": 8500,
  "requests_get": 8000,
  "requests_put": 450,
  "status_4xx": 23,
  "status_5xx": 2,
  "bytes_sent": 104857600,
  "unique_ips": 45
}
```

## Security

- **API Key Protection**: Set `APP_API_KEY` to require authentication
- **Rate Limiting**: Token bucket algorithm (configurable RPS and burst)
- **Input Validation**: All tool parameters are validated
- **Safe Limits**: Max log bytes, max scan lines, max objects returned
- **No Raw Log Exposure**: Frontend never accesses logs directly

## Deployment

### Docker (Production)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY static/ static/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t spacewatch .
docker run -p 8000:8000 --env-file .env spacewatch
```

### Enable Automatic Snapshots

For production monitoring, enable the scheduler:

```bash
ENABLE_SCHEDULER=true
SNAPSHOT_EVERY_SEC=300
SCHEDULER_SOURCE_BUCKETS=bucket1,bucket2,bucket3
```

This will capture metrics every 5 minutes for the specified buckets.

### Multiple Replicas (Leader Election)

If running multiple instances, designate one leader for scheduling:

```bash
# Instance 1 (leader)
SCHEDULER_INSTANCE_ID=instance-1
SCHEDULER_LEADER_ID=instance-1

# Instance 2 (follower)
SCHEDULER_INSTANCE_ID=instance-2
SCHEDULER_LEADER_ID=instance-1
```

## Troubleshooting

### "Cannot list buckets" Error

If you get this error, your Spaces key might be scoped to specific buckets. Set:
```bash
FALLBACK_BUCKETS=bucket1,bucket2,bucket3
```

### No Metrics Available

Ensure:
1. `METRICS_BUCKET` exists and is writable
2. Run manual snapshot: `POST /metrics/snapshot?source_bucket=my-bucket`
3. Enable scheduler: `ENABLE_SCHEDULER=true`

### Access Logs Not Found

1. Verify `ACCESS_LOGS_BUCKET` and `ACCESS_LOGS_ROOT_PREFIX` are correct
2. Check that access logging is enabled on your Spaces buckets
3. Access logs may take up to an hour to appear in DigitalOcean Spaces

### AI Not Responding

Check:
1. `DO_AGENT_URL` is correct and accessible
2. `DO_AGENT_KEY` is valid
3. Network connectivity to the AI endpoint
4. Check logs for specific error messages

## Development

### Run in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Project Structure

```
spacewatch/
├── main.py              # FastAPI backend with AI tool framework
├── requirements.txt     # Python dependencies
├── sample.env          # Example environment configuration
├── static/
│   └── index.html      # Web dashboard (Vue.js-free, vanilla JS)
└── README.md           # This file
```

### Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **httpx**: HTTP client for AI agent calls
- **boto3**: AWS/S3 SDK for DigitalOcean Spaces
- **matplotlib**: Chart generation (server-side)
- **pydantic**: Data validation

## Performance

- **Bucket Cache**: 5-minute TTL to reduce list_buckets calls
- **Rate Limiting**: Prevents API abuse
- **Paginated Results**: Max objects/lines configurable
- **Compressed Metrics**: Gzip compression for storage efficiency
- **Top IPs Cache**: 2-minute TTL for rendered charts

## Limitations

- SpaceWatch can only answer questions from:
  - Spaces object listings (sizes, last_modified)
  - Access logs stored in `ACCESS_LOGS_BUCKET`
  - Metrics snapshots in `METRICS_BUCKET`
- It cannot provide AWS CloudWatch or Azure Monitor metrics without additional integrations
- S3 listings are not guaranteed ordered by last_modified (SpaceWatch sorts client-side)
- Access logs may contain URL-encoded keys (spaces become `%20`)

## License

This project is open source. Please check with the repository owner for licensing details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- Built with FastAPI and Chart.js
- AI-powered by OpenAI-compatible APIs
- Storage via DigitalOcean Spaces (S3-compatible)
