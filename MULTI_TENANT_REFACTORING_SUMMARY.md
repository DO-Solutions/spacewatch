# Multi-Tenant Refactoring Summary

This document summarizes the complete multi-tenant refactoring of main.py to support per-request credentials.

## Changes Made

### 1. Credential Handling
- **Removed:** Global SPACES_KEY and SPACES_SECRET environment variables
- **Added:** Per-request credential handling via ChatRequest and HTTP headers
- **Security:** Used `SecretStr` from pydantic to prevent accidental credential exposure
- **Validation:** Added credential validation in `create_s3_client` to ensure credentials are not empty

### 2. S3 Client Creation
- **Function:** `create_s3_client(access_key, secret_key, region, endpoint)`
- Creates a new boto3 S3 client for each request with user-provided credentials
- Validates credentials are not empty before creating client
- Supports optional region and endpoint overrides

### 3. Updated Functions
The following functions were updated to accept per-request parameters:

#### Core Functions:
- `_put_metrics_line(s3_client, bucket, key, line, log_bucket, metrics_bucket)`
- `compute_request_metrics_from_logs(s3_client, source_bucket, log_bucket, log_prefix)`
- `run_metrics_snapshot(s3_client, source_bucket, source_prefix, log_bucket, log_prefix, metrics_bucket, metrics_prefix)`
- `storage_summary(s3_client, bucket, prefix, log_bucket, metrics_bucket)`

#### Metrics Functions:
- `metrics_sources_internal(s3_client, metrics_bucket, metrics_prefix, hours, log_bucket)`
- `metrics_series_internal(s3_client, source_bucket, metrics_bucket, metrics_prefix, source_prefix, limit, hours, log_bucket)`
- `_metrics_key_for_ts(ts, metrics_prefix)`

#### Log Functions:
- `read_log_object(s3_client, bucket, key, tail_lines, log_bucket, metrics_bucket)`
- `list_access_log_objects_for_source(s3_client, source_bucket, log_bucket, log_prefix, date_yyyy_mm_dd, max_items, metrics_bucket)`
- `search_access_logs(s3_client, source_bucket, log_bucket, log_prefix, contains, method, object_key, status_prefix, date_yyyy_mm_dd, limit_matches, metrics_bucket)`
- `object_audit_timeline(s3_client, source_bucket, object_key, log_bucket, log_prefix, hours, limit, methods, metrics_bucket)`

#### Cache Functions:
- `refresh_bucket_cache(s3_client, force, log_bucket, metrics_bucket)`
- `require_bucket_allowed(bucket, s3_client, log_bucket, metrics_bucket)`
- `list_objects(s3_client, bucket, prefix, max_items, log_bucket, metrics_bucket)`
- `recent_objects(s3_client, bucket, prefix, limit, log_bucket, metrics_bucket)`

### 4. Tools Refactoring
- **Before:** Static TOOLS dictionary with global credentials
- **After:** `_build_tools(ctx)` function that creates tools with context
- **Context includes:**
  - `s3_client`: Per-request S3 client
  - `log_bucket`: User's access logs bucket
  - `log_prefix`: Access logs prefix
  - `metrics_bucket`: User's metrics bucket
  - `metrics_prefix`: Metrics prefix

All 12 tools now operate with per-request credentials:
1. `buckets` - List allowed buckets
2. `list_objects` - List objects in bucket
3. `recent_objects` - Recent objects by last_modified
4. `storage_summary` - Total bytes/objects
5. `top_largest` - Largest objects by size
6. `snapshot` - Write metrics snapshot
7. `metrics_sources` - Discover source buckets
8. `metrics_series` - Get time series data
9. `list_access_logs` - List log files
10. `read_log` - Read log file
11. `search_logs` - Search access logs
12. `object_audit` - Object audit timeline

### 5. HTTP Endpoints Updated

#### /chat Endpoint
```python
@app.post("/chat")
def chat(req: ChatRequest, ...):
    # Extract credentials from request
    s3_client = create_s3_client(
        req.spaces_key.get_secret_value(),
        req.spaces_secret.get_secret_value(),
        req.region,
        req.endpoint
    )
    
    # Build context
    tool_ctx = {
        "s3_client": s3_client,
        "log_bucket": req.log_bucket,
        "log_prefix": req.log_prefix or "",
        "metrics_bucket": req.metrics_bucket,
        "metrics_prefix": req.metrics_prefix or "spacewatch-metrics/",
    }
    
    # Pass context to tools
    tool_result = _execute_tool(tool, args, tool_ctx)
```

#### Tool Endpoints
All `/tools/*` endpoints now accept credentials via headers:
- `X-Spaces-Key` (required)
- `X-Spaces-Secret` (required)
- `X-Log-Bucket` (optional)
- `X-Metrics-Bucket` (optional)
- `X-Region` (optional)
- `X-Endpoint` (optional)

Examples:
- `/tools/buckets` - List buckets
- `/tools/storage-summary` - Storage summary
- `/tools/list-all` - List all objects
- `/tools/top-largest` - Top largest objects

#### Metrics Endpoints
All `/metrics/*` endpoints now accept credentials via headers:
- `X-Spaces-Key` (required)
- `X-Spaces-Secret` (required)
- `X-Metrics-Bucket` (required for most endpoints)
- `X-Metrics-Prefix` (optional)
- `X-Log-Bucket` (optional)
- `X-Region` (optional)
- `X-Endpoint` (optional)

Examples:
- `/metrics/sources` - Discover source buckets
- `/metrics/series` - Get time series data
- `/metrics/aggregate-series` - Aggregated metrics
- `/metrics/snapshot` - Create snapshot

#### Plot Endpoints
- `/plots/top-ips.png` - Now accepts credentials via headers

### 6. ChatRequest Model
```python
class ChatRequest(BaseModel):
    message: str
    spaces_key: SecretStr  # Protected from accidental exposure
    spaces_secret: SecretStr  # Protected from accidental exposure
    log_bucket: Optional[str] = None
    log_prefix: Optional[str] = ""
    metrics_bucket: Optional[str] = None
    metrics_prefix: Optional[str] = "spacewatch-metrics/"
    region: Optional[str] = None
    endpoint: Optional[str] = None
```

### 7. Scheduler Changes
- **Status:** Disabled in multi-tenant mode
- **Reason:** Scheduler requires global credentials which are no longer available
- **Warning:** Application logs a warning if ENABLE_SCHEDULER=true in multi-tenant mode
- **Alternative:** Users can trigger snapshots via `/metrics/snapshot` endpoint with their credentials

### 8. Security Improvements
1. **No credential logging:** Used `SecretStr` to prevent credentials from appearing in logs/repr
2. **Credential validation:** Empty or None credentials are rejected with clear error messages
3. **Bucket validation:** All functions validate required buckets are provided before use
4. **Type safety:** Updated function signatures to use `Optional[str]` for accurate type hints
5. **No persistence:** Credentials are never stored, cached, or persisted anywhere

### 9. Migration Guide

#### Old Usage (Global Credentials):
```env
SPACES_KEY=my-key
SPACES_SECRET=my-secret
ACCESS_LOGS_BUCKET=my-logs
METRICS_BUCKET=my-metrics
```

#### New Usage (Per-Request):

**For /chat endpoint:**
```json
POST /chat
{
  "message": "Show me recent files",
  "spaces_key": "my-key",
  "spaces_secret": "my-secret",
  "log_bucket": "my-logs",
  "log_prefix": "logs/",
  "metrics_bucket": "my-metrics",
  "metrics_prefix": "metrics/"
}
```

**For /tools/* endpoints:**
```bash
curl -H "X-Spaces-Key: my-key" \
     -H "X-Spaces-Secret: my-secret" \
     -H "X-Log-Bucket: my-logs" \
     -H "X-Metrics-Bucket: my-metrics" \
     /tools/buckets
```

**For /metrics/* endpoints:**
```bash
curl -H "X-Spaces-Key: my-key" \
     -H "X-Spaces-Secret: my-secret" \
     -H "X-Metrics-Bucket: my-metrics" \
     -H "X-Metrics-Prefix: metrics/" \
     /metrics/sources
```

## Testing

### Code Quality
- ✅ No syntax errors
- ✅ No type errors
- ✅ CodeQL security scan: 0 alerts
- ✅ Application imports successfully
- ✅ All 12 tools build successfully with context

### Security
- ✅ SecretStr properly masks credentials in logs/repr
- ✅ Empty credentials are rejected with clear error
- ✅ Bucket validation prevents None errors
- ✅ No global credentials used anywhere

## Benefits

1. **Multi-tenant support:** Multiple users can use the same application with different credentials
2. **Security:** Credentials are per-request, not stored globally
3. **Flexibility:** Each request can specify different buckets, regions, endpoints
4. **Isolation:** One user's operations don't affect another user's
5. **Scalability:** Application can serve many tenants simultaneously

## Breaking Changes

1. **Environment variables removed:**
   - `SPACES_KEY` - Now per-request
   - `SPACES_SECRET` - Now per-request
   - Note: `ACCESS_LOGS_BUCKET` and `METRICS_BUCKET` were already commented as "no longer global defaults"

2. **Scheduler disabled:**
   - Can no longer run automatic snapshots without credentials
   - Users must trigger snapshots via API with their credentials

3. **API changes:**
   - `/chat` endpoint requires credentials in request body
   - All `/tools/*` endpoints require credentials in headers
   - All `/metrics/*` endpoints require credentials in headers

## Non-Breaking Changes

1. **Environment variables retained:**
   - `DEFAULT_SPACES_REGION` - Default region if not specified per-request
   - `DEFAULT_SPACES_ENDPOINT` - Default endpoint if not specified per-request
   - All other configuration (rate limits, cache TTL, safety limits, etc.)

2. **Backward compatibility:**
   - `FALLBACK_BUCKETS` still works for scoped keys
   - `/health` endpoint still works (no credentials required)
   - `/stats` endpoint behavior unchanged

## Conclusion

The multi-tenant refactoring is complete and secure. The application now supports:
- ✅ Per-request credentials
- ✅ Multiple tenants with isolated operations
- ✅ Comprehensive security validation
- ✅ No credential exposure or persistence
- ✅ Clean separation of concerns
- ✅ Zero security vulnerabilities (CodeQL scan)
