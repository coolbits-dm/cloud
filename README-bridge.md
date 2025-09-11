# @oPipe® Bridge - Zero-Trust Gateway Documentation

## Overview

The @oPipe® Bridge provides a secure, zero-trust interface between external clients and the internal `str.py` system. This bridge ensures that `str.py` remains completely private with no external access, while providing a stable interface for GPU inference and routing.

**Key Principles:**
- **Zero-Trust**: Everything signed, everything logged, fail-closed
- **Private**: `str.py` remains private - no reading, no dumping, no LLM training
- **Minimal Interface**: Stable, minimal interface for GPU inference through @oPipe®

## Security Model

### Authentication & Authorization

All requests must include the following headers:

```
X-Client-Id: <CLIENT_ID>
X-Timestamp: <unix_ms>
X-Nonce: <uuid4>
Authorization: Bearer <API_KEY>
X-Signature: hex(HMAC_SHA256(HMAC_KEY, method|path|X-Timestamp|X-Nonce|sha256(body)))
X-Key-Id: <kid>  # Optional, defaults to 'v1'
```

### HMAC Signature Calculation

```python
import hmac
import hashlib
import time
import uuid

def calculate_signature(method, path, timestamp, nonce, body, hmac_key):
    body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
    message = f"{method}|{path}|{timestamp}|{nonce}|{body_hash}"
    signature = hmac.new(
        hmac_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature
```

### IP Allowlist

Only requests from IPs in the configured CIDR allowlist are accepted. CORS is disabled - this is server-to-server communication only.

### Rate Limiting

- **Rate Limit**: 60 requests per second per CLIENT_ID
- **Burst Limit**: 120 requests per second per CLIENT_ID
- **Timeout**: 120 seconds hard timeout

## Configuration

### Environment Variables

```bash
CLIENT_ID=<OGPT_BRIDGE_ID>
HMAC_KEY=<OGPT_BRIDGE_HMAC_BASE64>  # Base64 encoded HMAC key
API_KEY=<OGPT_BRIDGE_APIKEY>
ALLOWLIST_IPS=<CIDR_LIST>  # Comma-separated CIDR blocks
MTLS_CA=<BASE64_PEM_CA>  # Optional mTLS CA certificate
```

### Key Rotation

The system supports up to 2 active key pairs simultaneously:
- **Key IDs**: `v1`, `v2`
- **TTL**: Maximum 30 days per key
- **Rotation**: New keys can be added while old ones remain active

## API Endpoints

### POST /_bridge/v1/route

Main routing endpoint for OpenAI-compatible requests.

**Request Body:**
```json
{
  "path": "/v1/chat/completions" | "/v1/embeddings" | "/v1/completions",
  "payload": {
    // OpenAI-compatible payload
  },
  "prefs": {
    "gpu": true,
    "tp": 1,
    "max_tokens": 2048
  }
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    // OpenAI-compatible response
  },
  "trace": {
    "lat_ms": 150,
    "model": "qwen2.5-7b-instruct"
  }
}
```

### GET /_bridge/v1/healthz

Health check endpoint.

**Response:**
```json
{
  "ok": true,
  "cuda": true,
  "gpus": [
    {
      "name": "NVIDIA A100-SXM4-80GB",
      "mem_gb": 80
    }
  ]
}
```

### GET /_bridge/v1/models

List available models.

**Response:**
```json
{
  "data": [
    {
      "id": "qwen2.5-7b-instruct",
      "dtype": "auto",
      "device": "cuda"
    },
    {
      "id": "qwen2.5-14b-instruct",
      "dtype": "auto",
      "device": "cuda"
    }
  ]
}
```

### POST /_bridge/v1/encode

Encode object to strict JSON string.

**Request:**
```json
{
  "txt": {
    "message": "Hello, world!",
    "data": [1, 2, 3]
  }
}
```

**Response:**
```json
{
  "ok": true,
  "json": "{\"message\":\"Hello, world!\",\"data\":[1,2,3]}"
}
```

### POST /_bridge/v1/decode

Decode JSON string to object.

**Request:**
```json
{
  "json": "{\"message\":\"Hello, world!\",\"data\":[1,2,3]}"
}
```

**Response:**
```json
{
  "ok": true,
  "obj": {
    "message": "Hello, world!",
    "data": [1, 2, 3]
  }
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `BRIDGE_INVALID_PAYLOAD` | 400 | Invalid or malformed payload |
| `BRIDGE_AUTH_FAILED` | 401 | Authentication failed |
| `BRIDGE_NOT_ALLOWED` | 403 | IP not in allowlist |
| `BRIDGE_TIMEOUT` | 408 | Request timeout |
| `BRIDGE_BUSY` | 409 | Rate limit exceeded |
| `BRIDGE_MODEL_UNSUPPORTED` | 422 | Unsupported model or path |
| `BRIDGE_BACKEND_ERROR` | 500 | Internal backend error |

**Error Response Format:**
```json
{
  "ok": false,
  "code": "BRIDGE_AUTH_FAILED",
  "msg": "Invalid signature",
  "trace": {
    "rid": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## GPU Policy

### GPU Usage Rules

1. **Prefer GPU**: Use CUDA if `torch.cuda.is_available()` and `prefs.gpu=true`
2. **CPU Fallback**: Use CPU-only if:
   - `prefs.gpu=false` is explicitly set
   - GPU resources are unavailable
   - GPU memory is insufficient
3. **Model Parameters**: Parameters from payload take priority over preferences
4. **Unsafe Values**: Unsafe parameter values are overridden for security

### GPU Status Check

```bash
# Check GPU availability
curl -H "Authorization: Bearer <API_KEY>" \
     -H "X-Client-Id: <CLIENT_ID>" \
     -H "X-Timestamp: $(date +%s%3N)" \
     -H "X-Nonce: $(uuidgen)" \
     -H "X-Signature: <calculated>" \
     https://<HOST>/_bridge/v1/healthz
```

## Usage Examples

### Chat Completions

```bash
curl -X POST https://<INTERNAL_HOST>/_bridge/v1/route \
  -H "Authorization: Bearer <API_KEY>" \
  -H "X-Client-Id: <CLIENT_ID>" \
  -H "X-Timestamp: $(date +%s%3N)" \
  -H "X-Nonce: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -H "X-Signature: <calculated>" \
  -d '{
    "path": "/v1/chat/completions",
    "payload": {
      "model": "qwen2.5-7b-instruct",
      "messages": [
        {"role": "user", "content": "Hello, how are you?"}
      ],
      "temperature": 0.7,
      "max_tokens": 1024,
      "stream": false
    },
    "prefs": {
      "gpu": true,
      "tp": 1
    }
  }'
```

### Streaming Chat Completions

```bash
curl -N -X POST https://<INTERNAL_HOST>/_bridge/v1/route \
  -H "Authorization: Bearer <API_KEY>" \
  -H "X-Client-Id: <CLIENT_ID>" \
  -H "X-Timestamp: $(date +%s%3N)" \
  -H "X-Nonce: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -H "X-Signature: <calculated>" \
  -d '{
    "path": "/v1/chat/completions",
    "payload": {
      "model": "qwen2.5-7b-instruct",
      "messages": [
        {"role": "user", "content": "Tell me a story"}
      ],
      "stream": true
    },
    "prefs": {
      "gpu": true
    }
  }'
```

### Embeddings

```bash
curl -X POST https://<INTERNAL_HOST>/_bridge/v1/route \
  -H "Authorization: Bearer <API_KEY>" \
  -H "X-Client-Id: <CLIENT_ID>" \
  -H "X-Timestamp: $(date +%s%3N)" \
  -H "X-Nonce: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -H "X-Signature: <calculated>" \
  -d '{
    "path": "/v1/embeddings",
    "payload": {
      "model": "qwen2.5-7b-instruct",
      "input": "This is a test sentence for embedding."
    },
    "prefs": {
      "gpu": true
    }
  }'
```

## Audit Logging

All requests are logged in JSON format with the following fields:

```json
{
  "time": "2025-09-07T15:30:45.123Z",
  "rid": "550e8400-e29b-41d4-a716-446655440000",
  "client_id": "OGPT_BRIDGE_ID",
  "ip": "192.168.1.100",
  "path": "/v1/chat/completions",
  "model": "qwen2.5-7b-instruct",
  "lat_ms": 150,
  "tokens_in": 25,
  "tokens_out": 50,
  "gpu": true,
  "rc": "200",
  "body_sha256": "a1b2c3d4e5f6..."
}
```

**Log Fields:**
- `time`: ISO timestamp
- `rid`: Request ID (UUID)
- `client_id`: Client identifier
- `ip`: Client IP address
- `path`: Request path
- `model`: Model used
- `lat_ms`: Latency in milliseconds
- `tokens_in`: Input tokens
- `tokens_out`: Output tokens
- `gpu`: Whether GPU was used
- `rc`: Response code
- `body_sha256`: SHA256 hash of request body (not logged in full)

## Testing Requirements

### Mandatory Tests

1. **Large Payload Test**: Payload >1MB
2. **Unicode Edge Cases**: Special characters, emojis, mixed scripts
3. **Stream Backpressure**: Streaming with slow clients
4. **GPU Saturation**: Behavior when GPU is fully utilized
5. **Rate Limiting**: Burst and sustained rate limits
6. **Authentication**: HMAC signature validation
7. **IP Allowlist**: CIDR-based access control

### Test Script Example

```python
#!/usr/bin/env python3
import requests
import json
import time
import uuid
import hmac
import hashlib

def test_large_payload():
    """Test with payload >1MB"""
    large_data = {
        'content': 'x' * (1024 * 1024),  # 1MB
        'metadata': {'test': True}
    }
    
    payload = {
        'path': '/v1/chat/completions',
        'payload': {
            'model': 'qwen2.5-7b-instruct',
            'messages': [{'role': 'user', 'content': large_data['content']}]
        },
        'prefs': {'gpu': True}
    }
    
    # Make request with proper authentication
    # ... (authentication code)
    
def test_unicode_edge_cases():
    """Test Unicode handling"""
    unicode_tests = [
        '🚀 Hello 世界! ñáéíóú',
        'Mix: 中文 + English + 123 + 🎯',
        'Control chars: Line1\nLine2\tTabbed',
        'Symbols: !@#$%^&*()_+-=[]{}|;:,.<>?'
    ]
    
    for test_text in unicode_tests:
        payload = {
            'path': '/v1/chat/completions',
            'payload': {
                'model': 'qwen2.5-7b-instruct',
                'messages': [{'role': 'user', 'content': test_text}]
            },
            'prefs': {'gpu': True}
        }
        
        # Make request with proper authentication
        # ... (authentication code)
```

## Deployment

### Prerequisites

- Python ≥3.10
- PyTorch with CUDA support (optional)
- Flask
- Valid SSL certificates for production

### Installation

```bash
# Install dependencies
pip install flask torch requests

# Set environment variables
export CLIENT_ID="OGPT_BRIDGE_ID"
export HMAC_KEY="OGPT_BRIDGE_HMAC_BASE64"
export API_KEY="OGPT_BRIDGE_APIKEY"
export ALLOWLIST_IPS="127.0.0.1/32,10.0.0.0/8"

# Run bridge
python opipe_bridge.py
```

### Production Deployment

```bash
# Use production WSGI server
gunicorn -w 4 -b 0.0.0.0:8080 opipe_bridge:app

# Or with systemd service
sudo systemctl enable opipe-bridge
sudo systemctl start opipe-bridge
```

## Security Considerations

1. **Key Management**: Store HMAC keys securely, rotate regularly
2. **Network Security**: Use VPN or private networks for communication
3. **Monitoring**: Monitor audit logs for suspicious activity
4. **Updates**: Keep dependencies updated for security patches
5. **Backup**: Regular backup of configuration and logs

## Support

For technical support or questions about the @oPipe® Bridge:

- **Internal Documentation**: This README
- **Audit Logs**: Check JSON logs for debugging
- **Health Endpoint**: Use `/healthz` for status checks
- **Model Endpoint**: Use `/models` for available models

---

**@oPipe® Bridge - Zero-Trust Gateway**  
CoolBits.ai / cbLM.ai - Internal Bridge System  
Company: COOL BITS SRL
