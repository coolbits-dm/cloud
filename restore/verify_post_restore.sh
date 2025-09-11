#!/bin/bash
# CoolBits.ai Post-Restore Verification Script
# ===========================================

set -e

echo "🔍 CoolBits.ai Post-Restore Verification"
echo "========================================"

# Configuration
DASHBOARD_URL="http://localhost:8081"
BRIDGE_URL="http://localhost:8101"
MAX_RETRIES=5
RETRY_DELAY=10

# Function to test endpoint with retries
test_endpoint() {
    local url="$1"
    local description="$2"
    local retries=0
    
    echo "  🔍 Testing $description ($url)..."
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -f -s "$url" >/dev/null 2>&1; then
            echo "    ✅ OK"
            return 0
        fi
        
        retries=$((retries + 1))
        if [ $retries -lt $MAX_RETRIES ]; then
            echo "    ⏳ Retry $retries/$MAX_RETRIES in ${RETRY_DELAY}s..."
            sleep $RETRY_DELAY
        fi
    done
    
    echo "    ❌ FAILED after $MAX_RETRIES attempts"
    return 1
}

# Function to get JSON response
get_json_response() {
    local url="$1"
    curl -s "$url" 2>/dev/null || echo "{}"
}

# 1. Test basic connectivity
echo "🌐 Testing basic connectivity..."
if test_endpoint "$DASHBOARD_URL/api/health" "Dashboard Health"; then
    DASHBOARD_OK=true
else
    DASHBOARD_OK=false
fi

if test_endpoint "$BRIDGE_URL/health" "Bridge Health"; then
    BRIDGE_OK=true
else
    BRIDGE_OK=false
fi

# 2. Test critical endpoints
echo ""
echo "🔧 Testing critical endpoints..."

# Dashboard endpoints
if [ "$DASHBOARD_OK" = true ]; then
    test_endpoint "$DASHBOARD_URL/api/services/status" "Services Status"
    test_endpoint "$DASHBOARD_URL/api/feature-flags" "Feature Flags"
    test_endpoint "$DASHBOARD_URL/api/health" "Health Check"
fi

# Bridge endpoints
if [ "$BRIDGE_OK" = true ]; then
    test_endpoint "$BRIDGE_URL/health" "Bridge Health"
    test_endpoint "$BRIDGE_URL/api/status" "Bridge Status"
fi

# 3. Verify service functionality
echo ""
echo "📊 Verifying service functionality..."

# Check dashboard health response
if [ "$DASHBOARD_OK" = true ]; then
    echo "  🏥 Checking dashboard health response..."
    HEALTH_RESPONSE=$(get_json_response "$DASHBOARD_URL/api/health")
    
    if echo "$HEALTH_RESPONSE" | jq -e '.status' >/dev/null 2>&1; then
        STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.status')
        VERSION=$(echo "$HEALTH_RESPONSE" | jq -r '.version // "unknown"')
        UPTIME=$(echo "$HEALTH_RESPONSE" | jq -r '.uptimeSec // "unknown"')
        
        echo "    ✅ Status: $STATUS"
        echo "    📦 Version: $VERSION"
        echo "    ⏰ Uptime: $UPTIME seconds"
        
        if [ "$STATUS" = "healthy" ]; then
            echo "    ✅ Dashboard is healthy"
        else
            echo "    ⚠️  Dashboard status: $STATUS"
        fi
    else
        echo "    ❌ Invalid health response format"
    fi
fi

# Check bridge health response
if [ "$BRIDGE_OK" = true ]; then
    echo "  🌉 Checking bridge health response..."
    BRIDGE_RESPONSE=$(get_json_response "$BRIDGE_URL/health")
    
    if echo "$BRIDGE_RESPONSE" | jq -e '.status' >/dev/null 2>&1; then
        BRIDGE_STATUS=$(echo "$BRIDGE_RESPONSE" | jq -r '.status')
        BRIDGE_PORT=$(echo "$BRIDGE_RESPONSE" | jq -r '.port // "unknown"')
        
        echo "    ✅ Status: $BRIDGE_STATUS"
        echo "    🔌 Port: $BRIDGE_PORT"
        
        if [ "$BRIDGE_STATUS" = "healthy" ]; then
            echo "    ✅ Bridge is healthy"
        else
            echo "    ⚠️  Bridge status: $BRIDGE_STATUS"
        fi
    else
        echo "    ❌ Invalid bridge health response format"
    fi
fi

# 4. Check services status
echo ""
echo "📋 Checking services status..."
if [ "$DASHBOARD_OK" = true ]; then
    SERVICES_RESPONSE=$(get_json_response "$DASHBOARD_URL/api/services/status")
    
    if echo "$SERVICES_RESPONSE" | jq -e '.services' >/dev/null 2>&1; then
        SERVICES_COUNT=$(echo "$SERVICES_RESPONSE" | jq -r '.services | keys | length')
        echo "    📊 Services count: $SERVICES_COUNT"
        
        # Check each service status
        echo "$SERVICES_RESPONSE" | jq -r '.services | to_entries[] | "\(.key): \(.value.status)"' | while read -r service_info; do
            echo "    🔧 $service_info"
        done
    else
        echo "    ❌ Invalid services response format"
    fi
fi

# 5. Check feature flags
echo ""
echo "🚩 Checking feature flags..."
if [ "$DASHBOARD_OK" = true ]; then
    FEATURE_FLAGS_RESPONSE=$(get_json_response "$DASHBOARD_URL/api/feature-flags")
    
    if echo "$FEATURE_FLAGS_RESPONSE" | jq -e '.flags' >/dev/null 2>&1; then
        TOTAL_FLAGS=$(echo "$FEATURE_FLAGS_RESPONSE" | jq -r '.flags | keys | length')
        ENABLED_FLAGS=$(echo "$FEATURE_FLAGS_RESPONSE" | jq -r '.enabled | keys | length')
        DISABLED_FLAGS=$(echo "$FEATURE_FLAGS_RESPONSE" | jq -r '.disabled | keys | length')
        
        echo "    📊 Total flags: $TOTAL_FLAGS"
        echo "    ✅ Enabled flags: $ENABLED_FLAGS"
        echo "    ❌ Disabled flags: $DISABLED_FLAGS"
        
        if [ $ENABLED_FLAGS -gt 0 ]; then
            echo "    🚩 Enabled flags:"
            echo "$FEATURE_FLAGS_RESPONSE" | jq -r '.enabled | keys[]' | while read -r flag; do
                echo "      - $flag"
            done
        fi
    else
        echo "    ❌ Invalid feature flags response format"
    fi
fi

# 6. Check runtime configuration
echo ""
echo "⚙️  Checking runtime configuration..."
if [ -f ".runtime.json" ]; then
    RUNTIME_CONFIG=$(cat .runtime.json)
    echo "    ✅ Runtime config file exists"
    
    if echo "$RUNTIME_CONFIG" | jq -e '.port' >/dev/null 2>&1; then
        PORT=$(echo "$RUNTIME_CONFIG" | jq -r '.port')
        BRIDGE_PORT=$(echo "$RUNTIME_CONFIG" | jq -r '.bridge_port // "unknown"')
        STARTED_AT=$(echo "$RUNTIME_CONFIG" | jq -r '.started_at // "unknown"')
        
        echo "    🔌 Dashboard port: $PORT"
        echo "    🌉 Bridge port: $BRIDGE_PORT"
        echo "    ⏰ Started at: $STARTED_AT"
    else
        echo "    ⚠️  Invalid runtime config format"
    fi
else
    echo "    ⚠️  Runtime config file not found"
fi

# 7. Check backup metadata
echo ""
echo "📋 Checking backup metadata..."
if [ -f "backup_metadata.json" ]; then
    BACKUP_METADATA=$(cat backup_metadata.json)
    echo "    ✅ Backup metadata exists"
    
    if echo "$BACKUP_METADATA" | jq -e '.timestamp' >/dev/null 2>&1; then
        BACKUP_TIME=$(echo "$BACKUP_METADATA" | jq -r '.timestamp')
        BACKUP_VERSION=$(echo "$BACKUP_METADATA" | jq -r '.version // "unknown"')
        FILES_COUNT=$(echo "$BACKUP_METADATA" | jq -r '.files_count // "unknown"')
        
        echo "    📅 Backup time: $BACKUP_TIME"
        echo "    📦 Backup version: $BACKUP_VERSION"
        echo "    📁 Files count: $FILES_COUNT"
    else
        echo "    ⚠️  Invalid backup metadata format"
    fi
else
    echo "    ⚠️  Backup metadata file not found"
fi

# 8. Final verification
echo ""
echo "🎯 Final verification summary..."

ALL_TESTS_PASSED=true

# Check if all critical services are responding
if [ "$DASHBOARD_OK" = false ]; then
    echo "  ❌ Dashboard not responding"
    ALL_TESTS_PASSED=false
fi

if [ "$BRIDGE_OK" = false ]; then
    echo "  ❌ Bridge not responding"
    ALL_TESTS_PASSED=false
fi

# Check if we have at least one working endpoint
if [ "$DASHBOARD_OK" = true ] || [ "$BRIDGE_OK" = true ]; then
    echo "  ✅ At least one service is responding"
else
    echo "  ❌ No services are responding"
    ALL_TESTS_PASSED=false
fi

# Final result
echo ""
if [ "$ALL_TESTS_PASSED" = true ]; then
    echo "✅ Post-restore verification completed successfully!"
    echo "🚀 System is ready for production use"
    exit 0
else
    echo "❌ Post-restore verification failed"
    echo "🔧 Some services are not responding correctly"
    exit 1
fi
