# Multi-Tenant API Usage Examples

This document provides practical examples of using the SpaceWatch multi-tenant API.

## Prerequisites

1. Your DigitalOcean Spaces access key and secret key
2. (Optional) A bucket containing access logs
3. (Optional) A bucket for storing metrics
4. SpaceWatch server running (e.g., `uvicorn main:app --host 0.0.0.0 --port 8000`)

## Basic Setup

Set your credentials as environment variables (for convenience in examples):

```bash
export SPACES_KEY="your_spaces_access_key"
export SPACES_SECRET="your_spaces_secret_key"
export LOG_BUCKET="my-access-logs"
export METRICS_BUCKET="my-metrics"
export API_KEY="your_app_api_key"
```

## Example 1: List Your Buckets

```bash
curl -X GET "http://localhost:8000/tools/buckets" \
  -H "X-API-Key: ${API_KEY}" \
  -H "X-Spaces-Key: ${SPACES_KEY}" \
  -H "X-Spaces-Secret: ${SPACES_SECRET}"
```

Response:
```json
{
  "bucket_count": 3,
  "buckets": ["bucket1", "bucket2", "bucket3"]
}
```

## Example 2: List Objects in a Bucket

```bash
curl -X GET "http://localhost:8000/tools/list-all?bucket=my-bucket&prefix=uploads/" \
  -H "X-API-Key: ${API_KEY}" \
  -H "X-Spaces-Key: ${SPACES_KEY}" \
  -H "X-Spaces-Secret: ${SPACES_SECRET}" \
  -H "X-Log-Bucket: ${LOG_BUCKET}" \
  -H "X-Metrics-Bucket: ${METRICS_BUCKET}"
```

Response:
```json
{
  "bucket": "my-bucket",
  "prefix": "uploads/",
  "count": 42,
  "objects": [
    {
      "key": "uploads/file1.jpg",
      "size_bytes": 1048576,
      "size_human": "1.0 MB",
      "last_modified": "2026-01-28T12:34:56+00:00"
    }
  ],
  "truncated": false
}
```

## Example 3: Get Storage Summary

```bash
curl -X GET "http://localhost:8000/tools/storage-summary?bucket=my-bucket" \
  -H "X-API-Key: ${API_KEY}" \
  -H "X-Spaces-Key: ${SPACES_KEY}" \
  -H "X-Spaces-Secret: ${SPACES_SECRET}" \
  -H "X-Log-Bucket: ${LOG_BUCKET}" \
  -H "X-Metrics-Bucket: ${METRICS_BUCKET}"
```

Response:
```json
{
  "bucket": "my-bucket",
  "prefix": "",
  "object_count": 150,
  "total_size_bytes": 5368709120,
  "total_size_human": "5.0 GB"
}
```

## Example 4: Find Largest Files

```bash
curl -X GET "http://localhost:8000/tools/top-largest?bucket=my-bucket&limit=5" \
  -H "X-API-Key: ${API_KEY}" \
  -H "X-Spaces-Key: ${SPACES_KEY}" \
  -H "X-Spaces-Secret: ${SPACES_SECRET}" \
  -H "X-Log-Bucket: ${LOG_BUCKET}" \
  -H "X-Metrics-Bucket: ${METRICS_BUCKET}"
```

Response:
```json
{
  "bucket": "my-bucket",
  "prefix": "",
  "limit": 5,
  "objects": [
    {
      "key": "videos/large-video.mp4",
      "size_bytes": 524288000,
      "size_human": "500.0 MB",
      "last_modified": "2026-01-27T10:00:00+00:00"
    }
  ]
}
```

## Example 5: AI Chat Query

Ask the AI assistant questions about your storage:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d "{
    \"message\": \"What are my largest files?\",
    \"spaces_key\": \"${SPACES_KEY}\",
    \"spaces_secret\": \"${SPACES_SECRET}\",
    \"log_bucket\": \"${LOG_BUCKET}\",
    \"metrics_bucket\": \"${METRICS_BUCKET}\"
  }"
```

Response:
```json
{
  "answer": "Your largest files are: 1) large-video.mp4 (500 MB), 2) backup.tar.gz (250 MB), 3) database.sql (100 MB)...",
  "tool_used": "top_largest",
  "bucket_used": "my-bucket"
}
```

## Example 6: Get Metrics Sources

List buckets that have metrics data:

```bash
curl -X GET "http://localhost:8000/metrics/sources?hours=24" \
  -H "X-API-Key: ${API_KEY}" \
  -H "X-Spaces-Key: ${SPACES_KEY}" \
  -H "X-Spaces-Secret: ${SPACES_SECRET}" \
  -H "X-Metrics-Bucket: ${METRICS_BUCKET}" \
  -H "X-Metrics-Prefix: spacewatch-metrics/"
```

Response:
```json
{
  "metrics_bucket": "my-metrics",
  "metrics_prefix": "spacewatch-metrics/",
  "hours": 24,
  "sources": [
    {
      "source_bucket": "my-bucket",
      "source_prefix": "",
      "snapshot_count": 48
    }
  ]
}
```

## Example 7: Get Metrics Time Series

```bash
curl -X GET "http://localhost:8000/metrics/series?source_bucket=my-bucket&hours=24&limit=100" \
  -H "X-API-Key: ${API_KEY}" \
  -H "X-Spaces-Key: ${SPACES_KEY}" \
  -H "X-Spaces-Secret: ${SPACES_SECRET}" \
  -H "X-Metrics-Bucket: ${METRICS_BUCKET}" \
  -H "X-Metrics-Prefix: spacewatch-metrics/"
```

Response:
```json
{
  "source_bucket": "my-bucket",
  "source_prefix": "",
  "hours": 24,
  "points": [
    {
      "ts": "2026-01-28T12:00:00+00:00",
      "object_count": 150,
      "total_size_bytes": 5368709120,
      "requests_total": 1234
    }
  ]
}
```

## Example 8: Health Check

Check application health:

```bash
curl -X GET "http://localhost:8000/health"
```

Response:
```json
{
  "ok": true,
  "status": "healthy",
  "uptime_seconds": 3600,
  "spaces_endpoint": "https://sgp1.digitaloceanspaces.com",
  "spaces_region": "sgp1",
  "api_key_protection": true,
  "storage_metrics": {
    "total_operations_5m": 42,
    "error_rate_percent": 0.5,
    "latency_p50_ms": 45.2,
    "latency_p95_ms": 120.5,
    "latency_p99_ms": 250.8
  }
}
```

## Python Example

Using the `requests` library:

```python
import requests

# Configuration
API_URL = "http://localhost:8000"
API_KEY = "your_app_api_key"
SPACES_KEY = "your_spaces_access_key"
SPACES_SECRET = "your_spaces_secret_key"

# Common headers
headers = {
    "X-API-Key": API_KEY,
    "X-Spaces-Key": SPACES_KEY,
    "X-Spaces-Secret": SPACES_SECRET,
}

# List buckets
response = requests.get(f"{API_URL}/tools/buckets", headers=headers)
buckets = response.json()
print(f"Found {buckets['bucket_count']} buckets")

# Get storage summary
response = requests.get(
    f"{API_URL}/tools/storage-summary",
    headers=headers,
    params={"bucket": "my-bucket"}
)
summary = response.json()
print(f"Total size: {summary['total_size_human']}")

# Chat with AI
chat_data = {
    "message": "What files were uploaded today?",
    "spaces_key": SPACES_KEY,
    "spaces_secret": SPACES_SECRET,
    "log_bucket": "my-logs",
    "metrics_bucket": "my-metrics"
}
response = requests.post(
    f"{API_URL}/chat",
    headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
    json=chat_data
)
answer = response.json()
print(f"AI: {answer['answer']}")
```

## JavaScript Example

Using `fetch`:

```javascript
const API_URL = "http://localhost:8000";
const API_KEY = "your_app_api_key";
const SPACES_KEY = "your_spaces_access_key";
const SPACES_SECRET = "your_spaces_secret_key";

// Common headers
const headers = {
  "X-API-Key": API_KEY,
  "X-Spaces-Key": SPACES_KEY,
  "X-Spaces-Secret": SPACES_SECRET,
};

// List buckets
async function listBuckets() {
  const response = await fetch(`${API_URL}/tools/buckets`, { headers });
  const data = await response.json();
  console.log(`Found ${data.bucket_count} buckets:`, data.buckets);
}

// Chat with AI
async function chatWithAI(message) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      ...headers,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      spaces_key: SPACES_KEY,
      spaces_secret: SPACES_SECRET,
      log_bucket: "my-logs",
      metrics_bucket: "my-metrics",
    }),
  });
  const data = await response.json();
  console.log("AI:", data.answer);
}

// Usage
listBuckets();
chatWithAI("Show me my largest files");
```

## Error Handling

Always handle errors appropriately:

```bash
# Example with proper error handling
response=$(curl -s -w "\n%{http_code}" -X GET "http://localhost:8000/tools/buckets" \
  -H "X-API-Key: ${API_KEY}" \
  -H "X-Spaces-Key: ${SPACES_KEY}" \
  -H "X-Spaces-Secret: ${SPACES_SECRET}")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
  echo "Success: $body"
else
  echo "Error (HTTP $http_code): $body"
fi
```

## Common Error Responses

### Missing Credentials (422)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["header", "X-Spaces-Key"],
      "msg": "Field required"
    }
  ]
}
```

### Invalid Credentials (403)
```json
{
  "detail": "Cannot list buckets with current Spaces credentials..."
}
```

### Bucket Not Found (403)
```json
{
  "detail": "Bucket not allowed/not found: my-bucket"
}
```

### Rate Limited (429)
```json
{
  "detail": "Rate limit exceeded"
}
```

## Tips

1. **Keep credentials secure**: Never commit credentials to version control
2. **Use HTTPS in production**: Always transmit credentials over HTTPS
3. **Rotate credentials regularly**: Change your Spaces credentials periodically
4. **Monitor rate limits**: The default is 2 requests/second with burst of 10
5. **Cache bucket lists**: Don't call `/tools/buckets` on every request
6. **Use log_bucket wisely**: Only specify if you have access logs enabled
7. **Set metrics_bucket**: Required for metrics operations and snapshots

## Next Steps

- See `MULTI_TENANT_REFACTORING_SUMMARY.md` for technical details
- See `SECURITY_SUMMARY.md` for security best practices
- See `README.md` for feature overview
- See `GETTING_STARTED.md` for enhancement details
