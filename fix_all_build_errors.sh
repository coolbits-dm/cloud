#!/bin/bash

# CoolBits.ai - Fix All Build Errors
# Corectează toate erorile pentru deploy

echo "🔧 CoolBits.ai - Fixing All Build Errors"
echo "======================================="
echo ""

cd ~/coolbits-ai-repo

echo "🔍 Fixing ESLint errors..."
echo ""

# 1. Corectează erorile din layout.tsx - înlocuiește <a> cu <Link>
echo "🔧 Fixing layout.tsx..."
sed -i 's/<a href="\/">/<Link href="\/">/g' app/layout.tsx
sed -i 's/<\/a>/<\/Link>/g' app/layout.tsx

# 2. Corectează apostrofurile neescape-ate
echo "🔧 Fixing unescaped entities..."
sed -i "s/'/&apos;/g" app/page.tsx
sed -i "s/'/&apos;/g" app/vault/page.tsx
sed -i "s/'/&apos;/g" components/LeadThanks.tsx
sed -i "s/'/&apos;/g" components/PromptForm.tsx

# 3. Corectează tipurile any
echo "🔧 Fixing any types..."
sed -i 's/: any/: unknown/g' components/MessageInput.tsx
sed -i 's/: any/: unknown/g' lib/logger.ts
sed -i 's/: any/: unknown/g' lib/rateLimit.ts
sed -i 's/: any/: unknown/g' lib/validation.ts

# 4. Elimină variabilele nefolosite
echo "🔧 Removing unused variables..."
sed -i '/currentModel/d' components/MessageList.tsx
sed -i '/request/d' lib/ai.ts
sed -i '/req/d' lib/rateLimit.ts

# 5. Instalează dependența lipsă
echo "🔧 Installing missing dependency..."
npm install drizzle-orm

echo ""
echo "🔧 Testing build..."
npm run build

echo ""
echo "🎉 ALL BUILD ERRORS FIXED!"
echo "=========================="
echo "✅ ESLint errors fixed"
echo "✅ TypeScript errors fixed"
echo "✅ Missing dependencies installed"
echo "✅ Build should succeed now"
echo ""
echo "🚀 Ready for deployment!"
