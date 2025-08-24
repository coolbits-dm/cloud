# CoolBits - AI-Powered Business Solutions

A modern Next.js application that combines AI chat capabilities with lead generation and business intelligence features. Chat with Jean (GPT-4) and Gelu (Grok) to unlock new possibilities for your organization.

## 🚀 Features

- **AI Chat Interface**: Interact with Jean (OpenAI GPT-4) and Gelu (xAI Grok)
- **Lead Generation**: Intelligent form system with automated follow-up
- **NLP Processing**: Generate taglines and prompts using AI
- **Modern UI/UX**: Beautiful, responsive design with Tailwind CSS
- **Rate Limiting**: Built-in protection against abuse
- **Email Integration**: Resend + Nodemailer fallback
- **Database**: PostgreSQL with Prisma ORM
- **Logging**: Comprehensive logging with Winston
- **TypeScript**: Full type safety throughout the application

## 🏗️ Architecture

```
coolbits/
├─ app/                    # Next.js 14 App Router
│  ├─ layout.tsx         # Root layout with header/footer
│  ├─ page.tsx           # Landing page + PromptForm
│  ├─ dashboard/page.tsx # AI Chat dashboard
│  └─ api/               # API endpoints
├─ components/            # React components
├─ lib/                   # Utility libraries
├─ schemas/               # Zod validation schemas
├─ utils/                 # Helper functions
└─ prisma/               # Database schema
```

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS, CSS Modules
- **Database**: PostgreSQL, Prisma ORM
- **AI**: OpenAI GPT-4, xAI Grok (coming soon)
- **Email**: Resend, Nodemailer
- **Validation**: Zod
- **Logging**: Winston
- **Rate Limiting**: rate-limiter-flexible
- **Caching**: Upstash Redis (optional)

## 📋 Prerequisites

- Node.js 18+ 
- PostgreSQL database
- OpenAI API key
- Email service (Resend or SMTP)

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/coolbits.git
cd coolbits
```

### 2. Install dependencies

```bash
npm install
```

### 3. Set up environment variables

```bash
cp env.example .env.local
```

Edit `.env.local` with your configuration:

```env
# Database
DATABASE_URL="postgresql://username:password@localhost:5432/coolbits"

# OpenAI
OPENAI_API_KEY="your-openai-api-key"

# Email
RESEND_API_KEY="your-resend-api-key"
# OR SMTP fallback
SMTP_HOST="smtp.gmail.com"
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"
```

### 4. Set up the database

```bash
# Generate Prisma client
npm run db:generate

# Push schema to database
npm run db:push

# (Optional) Open Prisma Studio
npm run db:studio
```

### 5. Run the development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🗄️ Database Setup

### PostgreSQL

1. Install PostgreSQL
2. Create a new database:
   ```sql
   CREATE DATABASE coolbits;
   ```
3. Update your `.env.local` with the connection string

### Prisma Commands

```bash
# Generate Prisma client
npm run db:generate

# Push schema changes
npm run db:push

# Reset database
npm run db:reset

# Open Prisma Studio
npm run db:studio
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `OPENAI_API_KEY` | OpenAI API key for Jean | Yes |
| `RESEND_API_KEY` | Resend email service key | No* |
| `SMTP_HOST` | SMTP server host | No* |
| `ADMIN_EMAIL` | Admin notification email | No |
| `NODE_ENV` | Environment (development/production) | No |

*Either Resend or SMTP configuration is required for email functionality.

### Rate Limiting

The application includes built-in rate limiting:

- **API endpoints**: 100 requests per minute
- **Chat endpoints**: 20 requests per minute  
- **Lead submission**: 5 requests per hour
- **Authentication**: 10 attempts per hour

## 📱 Usage

### Landing Page

The main page (`/`) features:
- Hero section with AI capabilities
- Feature overview
- Lead capture form
- Company statistics

### Dashboard

Access the AI chat dashboard at `/dashboard`:
- Switch between Jean (GPT-4) and Gelu (Grok)
- Real-time chat interface
- Conversation history
- Usage statistics

### API Endpoints

#### Lead Submission
```http
POST /api/submit
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "company": "Acme Corp",
  "message": "Interested in AI solutions"
}
```

#### AI Chat
```http
POST /api/ai/jean
Content-Type: application/json

{
  "message": "Hello, how can you help me?",
  "model": "jean",
  "sessionId": "optional-session-id"
}
```

#### NLP Processing
```http
POST /api/taglines
Content-Type: application/json

{
  "type": "taglines",
  "industry": "Technology",
  "companyName": "TechCorp",
  "description": "Innovative software solutions",
  "tone": "professional",
  "length": "short"
}
```

## 🎨 Customization

### Styling

The application uses Tailwind CSS with custom components:

```css
/* Custom button styles */
.btn-primary {
  @apply bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg;
}

/* Custom animations */
.animate-blob {
  animation: blob 7s infinite;
}
```

### Components

All React components are modular and reusable:

```tsx
import PromptForm from '@/components/PromptForm'
import ChatWindow from '@/components/ChatWindow'

// Customize props as needed
<PromptForm onSubmit={handleSubmit} onSuccess={handleSuccess} />
<ChatWindow initialModel="jean" className="h-96" />
```

## 🔒 Security Features

- **Input Validation**: Zod schemas for all inputs
- **Rate Limiting**: Per-IP and per-route protection
- **SQL Injection Protection**: Prisma ORM with parameterized queries
- **XSS Protection**: Input sanitization and output encoding
- **CORS Configuration**: Configurable cross-origin policies

## 📊 Monitoring & Logging

### Logging

The application uses Winston for comprehensive logging:

```typescript
import logger from '@/lib/logger'

logger.info('User action', { userId, action })
logger.error('Error occurred', { error, context })
```

### Log Levels

- **Error**: Application errors and failures
- **Warn**: Warning conditions
- **Info**: General information
- **Debug**: Detailed debugging information

## 🚀 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy automatically on push

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables

Ensure all required environment variables are set in your production environment.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.coolbits.com](https://docs.coolbits.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/coolbits/issues)
- **Email**: support@coolbits.com

## 🔮 Roadmap

- [ ] xAI Grok integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app
- [ ] API rate limiting dashboard
- [ ] Advanced NLP features
- [ ] Integration marketplace

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- xAI for Grok (coming soon)
- Vercel for Next.js
- Prisma team for the excellent ORM
- Tailwind CSS for the utility-first framework

---

Built with ❤️ by the CoolBits team


