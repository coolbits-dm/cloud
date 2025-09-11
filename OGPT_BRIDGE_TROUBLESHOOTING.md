# oGPT Bridge Service - Troubleshooting Guide

## Current Issue: "fetch failed" Error

The `ogpt-bridge-service` is returning a 500 error with "fetch failed" when trying to make external API calls to OpenAI and xAI.

### Root Cause Analysis

The error occurs because:
1. **Network Connectivity**: Cloud Run service cannot make outbound HTTP requests
2. **VPC Configuration**: VPC connector might not be properly configured
3. **IAM Permissions**: Service account might lack necessary permissions
4. **Firewall Rules**: Outbound traffic might be blocked

### Solutions

#### 1. Fix VPC Configuration

Run the fix script:
```bash
chmod +x fix_ogpt_bridge.sh
./fix_ogpt_bridge.sh
```

This script will:
- Update VPC connector configuration
- Set proper egress rules (`--vpc-egress=all-traffic`)
- Grant necessary IAM permissions
- Test the service endpoints

#### 2. Manual VPC Configuration

If the script doesn't work, manually configure:

```bash
# Update service with proper VPC settings
gcloud run services update ogpt-bridge-service \
  --region=europe-west1 \
  --vpc-connector=svpc-europe-west1 \
  --vpc-egress=all-traffic \
  --timeout=300
```

#### 3. Check IAM Permissions

Verify service account has proper permissions:

```bash
# Get service account
SERVICE_ACCOUNT=$(gcloud run services describe ogpt-bridge-service \
  --region=europe-west1 \
  --format='value(spec.template.spec.serviceAccountName)')

# Grant Secret Manager access
gcloud projects add-iam-policy-binding coolbits-ai \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

#### 4. Test Connectivity

Use the debug endpoint to test connectivity:

```bash
SERVICE_URL=$(gcloud run services describe ogpt-bridge-service \
  --region=europe-west1 \
  --format='value(status.url)')

# Test debug endpoint
curl -sSf "$SERVICE_URL/api/debug" | jq '.'
```

#### 5. Verify Secrets

Ensure API keys are properly stored in Secret Manager:

```bash
# List secrets
gcloud secrets list --filter="name:ogpt"

# Check specific secret
gcloud secrets describe openai_api_key_ogpt01
```

### Debug Endpoints

The service now includes debug endpoints:

- **Health**: `GET /api/v1/health`
- **Debug**: `GET /api/debug` - Tests external connectivity
- **Chat**: `POST /api/ai/chat?role=<role>`

### Testing

Run the test script to verify everything works:

```bash
chmod +x test_ogpt_bridge.sh
./test_ogpt_bridge.sh
```

### Common Issues

1. **VPC Connector Not Found**
   ```bash
   gcloud compute networks vpc-access connectors create svpc-europe-west1 \
     --region=europe-west1 \
     --network=default \
     --range=10.8.0.0/28
   ```

2. **Service Account Permissions**
   ```bash
   gcloud projects add-iam-policy-binding coolbits-ai \
     --member="serviceAccount:coolbits-ai@appspot.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

3. **API Not Enabled**
   ```bash
   gcloud services enable \
     vpcaccess.googleapis.com \
     secretmanager.googleapis.com
   ```

### Monitoring

Check service logs:
```bash
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=ogpt-bridge-service" \
  --limit=50 \
  --format="table(timestamp,severity,textPayload)"
```

### Next Steps

1. Run `fix_ogpt_bridge.sh`
2. Test with `test_ogpt_bridge.sh`
3. Check debug endpoint for connectivity issues
4. Verify secrets are accessible
5. Monitor logs for any remaining errors
