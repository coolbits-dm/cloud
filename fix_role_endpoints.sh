#!/bin/bash

# CoolBits.ai - Fix Role-based API Endpoints
# Corectează problemele din endpointuri

echo "🔧 CoolBits.ai - Fixing Role-based API Endpoints"
echo "================================================"
echo ""

# Navighează la repo
cd ~/coolbits-ai-repo

echo "🔍 Fixing individual role endpoints..."
echo ""

# Lista rolurilor
declare -A roles=(
    ["01"]="ceo"
    ["02"]="cto" 
    ["03"]="marketing"
    ["04"]="development"
    ["05"]="operations"
    ["06"]="finance"
    ["07"]="hr"
    ["08"]="product"
    ["09"]="security"
    ["10"]="customer"
    ["11"]="board"
    ["12"]="strategy"
)

# Corectează endpointuri individuale pentru fiecare rol
for role_id in "${!roles[@]}"; do
  role_name="${roles[$role_id]}"
  
  echo "🔧 Fixing endpoint for role ${role_id} (${role_name})..."
  
  cat > "app/api/roles/${role_id}/route.ts" << EOF
import { NextRequest, NextResponse } from 'next/server'
import { SecretManagerServiceClient } from '@google-cloud/secret-manager'

const client = new SecretManagerServiceClient()

// Define role constants
const ROLE_ID = '${role_id}'
const ROLE_NAME = '${role_name}'

interface RoleRequest {
  provider: 'xai' | 'openai'
  message: string
  sessionId?: string
}

async function getApiKey(role: string, provider: 'xai' | 'openai'): Promise<string> {
  try {
    const secretName = provider === 'xai' 
      ? \`xai_api_key_ogrok\${role}\` 
      : \`openai_api_key_ogpt\${role}\`
      
    const name = \`projects/coolbits-ai/secrets/\${secretName}/versions/latest\`
    
    const [version] = await client.accessSecretVersion({ name })
    return version.payload?.data?.toString() || ''
  } catch (error) {
    console.error(\`Error accessing secret for \${role}/\${provider}:\`, error)
    throw new Error(\`Failed to access API key for \${role}/\${provider}\`)
  }
}

async function callXAI(apiKey: string, message: string): Promise<any> {
  try {
    const response = await fetch('https://api.x.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': \`Bearer \${apiKey}\`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'grok-v4-2024-11-20',
        messages: [
          {
            role: 'system',
            content: \`You are the \${ROLE_NAME} (Role ID: \${ROLE_ID}) AI assistant for CoolBits.ai. Provide specialized responses based on your role.\`
          },
          {
            role: 'user',
            content: message
          }
        ],
        max_tokens: 1000,
        temperature: 0.7
      })
    })

    if (!response.ok) {
      throw new Error(\`xAI API error: \${response.status}\`)
    }

    const data = await response.json()
    return {
      response: data.choices[0]?.message?.content || 'No response from xAI',
      usage: data.usage
    }
  } catch (error) {
    console.error('xAI API call failed:', error)
    throw error
  }
}

async function callOpenAI(apiKey: string, message: string): Promise<any> {
  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': \`Bearer \${apiKey}\`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: [
          {
            role: 'system',
            content: \`You are the \${ROLE_NAME} (Role ID: \${ROLE_ID}) AI assistant for CoolBits.ai. Provide specialized responses based on your role.\`
          },
          {
            role: 'user',
            content: message
          }
        ],
        max_tokens: 1000,
        temperature: 0.7
      })
    })

    if (!response.ok) {
      throw new Error(\`OpenAI API error: \${response.status}\`)
    }

    const data = await response.json()
    return {
      response: data.choices[0]?.message?.content || 'No response from OpenAI',
      usage: data.usage
    }
  } catch (error) {
    console.error('OpenAI API call failed:', error)
    throw error
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: RoleRequest = await request.json()
    
    // Validare
    if (!body.provider || !body.message) {
      return NextResponse.json({
        success: false,
        error: 'Missing required fields: provider, message'
      }, { status: 400 })
    }

    // Verifică provider-ul
    if (!['xai', 'openai'].includes(body.provider)) {
      return NextResponse.json({
        success: false,
        error: 'Invalid provider. Must be xai or openai'
      }, { status: 400 })
    }

    console.log(\`Processing request for role \${ROLE_ID} (\${ROLE_NAME}) with provider \${body.provider}\`)

    // Obține cheia API
    const apiKey = await getApiKey(ROLE_ID, body.provider)
    
    if (!apiKey) {
      return NextResponse.json({
        success: false,
        error: \`No API key found for role \${ROLE_ID} and provider \${body.provider}\`
      }, { status: 500 })
    }

    // Generează session ID dacă nu există
    const sessionId = body.sessionId || \`session_\${ROLE_ID}_\${body.provider}_\${Date.now()}\`

    // Apelează API-ul corespunzător
    let result
    if (body.provider === 'xai') {
      result = await callXAI(apiKey, body.message)
    } else {
      result = await callOpenAI(apiKey, body.message)
    }

    return NextResponse.json({
      success: true,
      message: 'Response generated successfully',
      data: {
        response: result.response,
        sessionId,
        role: ROLE_ID,
        roleName: ROLE_NAME,
        provider: body.provider,
        usage: result.usage
      }
    })

  } catch (error) {
    console.error('Role API error:', error)
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Internal server error'
    }, { status: 500 })
  }
}

// Endpoint pentru informații despre rol
export async function GET() {
  return NextResponse.json({
    success: true,
    message: 'Role information',
    data: {
      roleId: ROLE_ID,
      roleName: ROLE_NAME,
      subdomain: \`\${ROLE_NAME}.roles.coolbits.ai\`,
      providers: ['xai', 'openai'],
      description: \`Specialized AI assistant for \${ROLE_NAME} role\`
    }
  })
}
EOF

  echo "✅ Fixed endpoint for role ${role_id}: /api/roles/${role_id}"
done

echo ""
echo "🔧 Creating test script for fixed endpoints..."
echo ""

# Creează script de testare pentru endpointurile corectate
cat > test_fixed_endpoints.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing Fixed Role-based API Endpoints"
echo "========================================="
echo ""

cd ~/coolbits-ai-repo

echo "🚀 Starting development server..."
npm run dev &
DEV_PID=$!

echo "⏳ Waiting for server to start..."
sleep 10

echo ""
echo "🧪 Testing fixed endpoints..."
echo ""

# Testează CEO endpoint cu OpenAI (mai sigur)
echo "📝 Testing CEO role with OpenAI provider..."
curl -X POST http://localhost:3000/api/roles/01 \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "message": "Hello, I am the CEO. What are our current business priorities?"
  }' \
  | jq '.'

echo ""
echo "📝 Testing CTO role with OpenAI provider..."
curl -X POST http://localhost:3000/api/roles/02 \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "message": "Hello, I am the CTO. What are our current technical challenges?"
  }' \
  | jq '.'

echo ""
echo "📝 Testing Marketing role with OpenAI provider..."
curl -X POST http://localhost:3000/api/roles/03 \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "message": "Hello, I am the Marketing Manager. What are our current marketing strategies?"
  }' \
  | jq '.'

echo ""
echo "🛑 Stopping development server..."
kill $DEV_PID

echo ""
echo "🎉 Fixed endpoints testing complete!"
EOF

chmod +x test_fixed_endpoints.sh

echo ""
echo "🎉 ROLE-BASED API ENDPOINTS FIXED!"
echo "=================================="
echo "✅ Fixed variable scope issues"
echo "✅ Added proper role constants"
echo "✅ Created test script for fixed endpoints"
echo ""
echo "📝 To test fixed endpoints:"
echo "  ./test_fixed_endpoints.sh"
echo ""
echo "🚀 Ready for testing!"
