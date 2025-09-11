# CoolBits.ai - Role-based API Endpoints
# Creează endpointuri pentru toate cele 12 roluri (oGrok + oGPT)

echo "🚀 CoolBits.ai - Creating Role-based API Endpoints"
echo "=================================================="
echo ""

# Navighează la repo
cd ~/coolbits-ai-repo

echo "📁 Creating API endpoints structure..."
echo ""

# Creează directorul pentru endpointuri
mkdir -p app/api/roles

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

# Creează endpointul principal pentru toate rolurile
cat > app/api/roles/route.ts << 'EOF'
import { NextRequest, NextResponse } from 'next/server'
import { SecretManagerServiceClient } from '@google-cloud/secret-manager'

const client = new SecretManagerServiceClient()

interface RoleRequest {
  role: string
  provider: 'xai' | 'openai'
  message: string
  sessionId?: string
}

interface RoleResponse {
  success: boolean
  message: string
  data?: {
    response: string
    sessionId: string
    role: string
    provider: string
    usage?: {
      promptTokens: number
      completionTokens: number
      totalTokens: number
    }
  }
  error?: string
}

async function getApiKey(role: string, provider: 'xai' | 'openai'): Promise<string> {
  try {
    const secretName = provider === 'xai' 
      ? `xai_api_key_ogrok${role}` 
      : `openai_api_key_ogpt${role}`
      
    const name = `projects/coolbits-ai/secrets/${secretName}/versions/latest`
    
    const [version] = await client.accessSecretVersion({ name })
    return version.payload?.data?.toString() || ''
  } catch (error) {
    console.error(`Error accessing secret for ${role}/${provider}:`, error)
    throw new Error(`Failed to access API key for ${role}/${provider}`)
  }
}

async function callXAI(apiKey: string, message: string): Promise<any> {
  try {
    const response = await fetch('https://api.x.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'grok-v4-2024-11-20',
        messages: [
          {
            role: 'system',
            content: 'You are a specialized AI assistant for CoolBits.ai. Provide helpful, accurate, and professional responses.'
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
      throw new Error(`xAI API error: ${response.status}`)
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
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: [
          {
            role: 'system',
            content: 'You are a specialized AI assistant for CoolBits.ai. Provide helpful, accurate, and professional responses.'
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
      throw new Error(`OpenAI API error: ${response.status}`)
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
    if (!body.role || !body.provider || !body.message) {
      return NextResponse.json({
        success: false,
        error: 'Missing required fields: role, provider, message'
      }, { status: 400 })
    }

    // Verifică dacă rolul este valid (01-12)
    if (!/^(0[1-9]|1[0-2])$/.test(body.role)) {
      return NextResponse.json({
        success: false,
        error: 'Invalid role. Must be 01-12'
      }, { status: 400 })
    }

    // Verifică provider-ul
    if (!['xai', 'openai'].includes(body.provider)) {
      return NextResponse.json({
        success: false,
        error: 'Invalid provider. Must be xai or openai'
      }, { status: 400 })
    }

    console.log(`Processing request for role ${body.role} with provider ${body.provider}`)

    // Obține cheia API
    const apiKey = await getApiKey(body.role, body.provider)
    
    if (!apiKey) {
      return NextResponse.json({
        success: false,
        error: `No API key found for role ${body.role} and provider ${body.provider}`
      }, { status: 500 })
    }

    // Generează session ID dacă nu există
    const sessionId = body.sessionId || `session_${body.role}_${body.provider}_${Date.now()}`

    // Apelează API-ul corespunzător
    let result
    if (body.provider === 'xai') {
      result = await callXAI(apiKey, body.message)
    } else {
      result = await callOpenAI(apiKey, body.message)
    }

    const response: RoleResponse = {
      success: true,
      message: 'Response generated successfully',
      data: {
        response: result.response,
        sessionId,
        role: body.role,
        provider: body.provider,
        usage: result.usage
      }
    }

    return NextResponse.json(response)

  } catch (error) {
    console.error('Role API error:', error)
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Internal server error'
    }, { status: 500 })
  }
}

// Endpoint pentru listarea rolurilor disponibile
export async function GET() {
  const roles = [
    { id: '01', name: 'CEO', subdomain: 'ceo.roles.coolbits.ai' },
    { id: '02', name: 'CTO', subdomain: 'cto.roles.coolbits.ai' },
    { id: '03', name: 'Marketing Manager', subdomain: 'marketing.roles.coolbits.ai' },
    { id: '04', name: 'Development Manager', subdomain: 'development.roles.coolbits.ai' },
    { id: '05', name: 'Operations Manager', subdomain: 'operations.roles.coolbits.ai' },
    { id: '06', name: 'Finance Manager', subdomain: 'finance.roles.coolbits.ai' },
    { id: '07', name: 'HR Manager', subdomain: 'hr.roles.coolbits.ai' },
    { id: '08', name: 'Product Manager', subdomain: 'product.roles.coolbits.ai' },
    { id: '09', name: 'Security Manager', subdomain: 'security.roles.coolbits.ai' },
    { id: '10', name: 'Customer Manager', subdomain: 'customer.roles.coolbits.ai' },
    { id: '11', name: 'Board', subdomain: 'board.roles.coolbits.ai' },
    { id: '12', name: 'Strategy Office Manager', subdomain: 'strategy.roles.coolbits.ai' }
  ]

  return NextResponse.json({
    success: true,
    message: 'Available roles',
    data: {
      roles,
      providers: ['xai', 'openai'],
      totalRoles: roles.length
    }
  })
}
EOF

echo "✅ Created main roles API endpoint: /api/roles"
echo ""

# Creează endpointuri individuale pentru fiecare rol
for role_id in "${!roles[@]}"; do
  role_name="${roles[$role_id]}"
  
  echo "📝 Creating endpoint for role ${role_id} (${role_name})..."
  
  mkdir -p "app/api/roles/${role_id}"
  
  cat > "app/api/roles/${role_id}/route.ts" << EOF
import { NextRequest, NextResponse } from 'next/server'
import { SecretManagerServiceClient } from '@google-cloud/secret-manager'

const client = new SecretManagerServiceClient()

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
            content: \`You are the \${role_name} (Role ID: \${role_id}) AI assistant for CoolBits.ai. Provide specialized responses based on your role.\`
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
            content: \`You are the \${role_name} (Role ID: \${role_id}) AI assistant for CoolBits.ai. Provide specialized responses based on your role.\`
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

    console.log(\`Processing request for role \${role_id} (\${role_name}) with provider \${body.provider}\`)

    // Obține cheia API
    const apiKey = await getApiKey('${role_id}', body.provider)
    
    if (!apiKey) {
      return NextResponse.json({
        success: false,
        error: \`No API key found for role \${role_id} and provider \${body.provider}\`
      }, { status: 500 })
    }

    // Generează session ID dacă nu există
    const sessionId = body.sessionId || \`session_\${role_id}_\${body.provider}_\${Date.now()}\`

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
        role: '${role_id}',
        roleName: '${role_name}',
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
      roleId: '${role_id}',
      roleName: '${role_name}',
      subdomain: '${role_name}.roles.coolbits.ai',
      providers: ['xai', 'openai'],
      description: 'Specialized AI assistant for ${role_name} role'
    }
  })
}
EOF

  echo "✅ Created endpoint for role ${role_id}: /api/roles/${role_id}"
done

echo ""
echo "🔧 Installing Google Cloud Secret Manager dependency..."
npm install @google-cloud/secret-manager

echo ""
echo "🎉 ROLE-BASED API ENDPOINTS CREATED!"
echo "====================================="
echo "✅ Main endpoint: /api/roles"
echo "✅ Individual endpoints: /api/roles/01 through /api/roles/12"
echo "✅ Secret Manager integration"
echo "✅ xAI and OpenAI provider support"
echo "✅ Role-specific system prompts"
echo ""
echo "📝 Usage examples:"
echo "  POST /api/roles - All roles"
echo "  POST /api/roles/01 - CEO role"
echo "  POST /api/roles/02 - CTO role"
echo "  ..."
echo ""
echo "🚀 Ready for testing!"
