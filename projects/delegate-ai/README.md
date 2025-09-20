# 🤖 Delegate.ai - Autonomous AI Chief of Staff

An intelligent AI system that acts as your autonomous chief of staff, managing tasks, scheduling, communications, and more through a multi-agent architecture.

## 🚀 Quick Deployment (2 minutes)

Deploy to Railway and Vercel with one command:

```bash
./deploy.sh
```

Or follow the detailed [Deployment Guide](DEPLOYMENT_GUIDE.md).

## 🏗️ Architecture

- **Backend**: FastAPI + PostgreSQL + Redis + WebSockets
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **AI System**: Multi-agent architecture with LangChain + OpenAI
- **Deployment**: Railway (Backend) + Vercel (Frontend)

## 📦 Project Structure

```
delegate-ai/
├── backend/          # FastAPI backend
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   ├── Dockerfile    # Container configuration
│   └── requirements.txt
├── frontend/         # Next.js frontend
│   ├── app/          # Next.js 14 app directory
│   ├── components/   # Reusable UI components
│   └── package.json
├── ai_system/        # Multi-agent AI system
│   ├── agents/       # Individual AI agents
│   └── core/         # Core orchestration
└── DEPLOYMENT_GUIDE.md
```

## 🔧 Features

### Backend API
- ✅ FastAPI with async/await support
- ✅ PostgreSQL with SQLAlchemy ORM
- ✅ Redis for caching and job queues
- ✅ WebSocket real-time communications
- ✅ JWT authentication with OAuth
- ✅ Celery background job processing
- ✅ Comprehensive API documentation

### Frontend Dashboard
- ✅ Modern Next.js 14 with App Router
- ✅ TypeScript for type safety
- ✅ Tailwind CSS + Radix UI components
- ✅ Real-time updates via Socket.io
- ✅ Responsive professional design
- ✅ Dark/light theme support

### AI System
- ✅ Multi-agent orchestration
- ✅ Task delegation and coordination
- ✅ Meeting preparation agent
- ✅ Communication agent
- ✅ Research and analysis agent
- ✅ Schedule optimization

## 🚀 Deployment Options

### Option 1: One-Click Deploy (Recommended)

1. Clone the repository
2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```
3. Follow the prompts to set up Railway and Vercel
4. Add your OpenAI API key to Railway environment variables
5. Your app is live! 🎉

### Option 2: Manual Deployment

Follow the detailed [Deployment Guide](DEPLOYMENT_GUIDE.md) for step-by-step instructions.

### Option 3: Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your settings
npm run dev
```

## 🔑 Environment Variables

### Required for Backend (Railway)
- `DATABASE_URL` - PostgreSQL connection (auto-provided)
- `REDIS_URL` - Redis connection (auto-provided)
- `SECRET_KEY` - JWT secret key
- `OPENAI_API_KEY` - Your OpenAI API key

### Required for Frontend (Vercel)
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_WS_URL` - WebSocket URL

See [environment templates](.env.production) for complete lists.

## 📊 Live URLs

After deployment, your application will be available at:

- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-backend.up.railway.app`
- **API Docs**: `https://your-backend.up.railway.app/docs`
- **Health Check**: `https://your-backend.up.railway.app/health`

## 🧪 Testing Deployment

Test your deployment with the included testing script:

```bash
./test-deployment.sh
```

## 🛠️ Development Tools

- **Backend Tests**: `cd backend && pytest`
- **Frontend Build**: `cd frontend && npm run build`
- **Type Checking**: `cd frontend && npm run type-check`
- **Database Migrations**: `cd backend && alembic upgrade head`

## 📖 API Documentation

Once deployed, visit `/docs` on your backend URL for interactive API documentation powered by FastAPI's automatic OpenAPI generation.

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**: Update `CORS_ORIGINS` in Railway to include your Vercel URL
2. **Database Connection**: Ensure PostgreSQL addon is connected in Railway
3. **WebSocket Issues**: Check that `NEXT_PUBLIC_WS_URL` uses `wss://` protocol
4. **Build Failures**: Check Vercel build logs for missing environment variables

### Getting Help

- Check the [Deployment Guide](DEPLOYMENT_GUIDE.md)
- View Railway logs: `railway logs`
- Check Vercel deployment logs in dashboard
- Test endpoints with the included test script

## 🎯 Hackathon Ready

This project is optimized for hackathon demos:

- ⚡ **Fast deployment** (< 5 minutes)
- 🎨 **Professional UI** with modern design
- 🤖 **AI-powered features** ready to showcase
- 📱 **Real-time updates** for impressive demos
- 🔒 **Production-ready** security and architecture
- 📊 **Live monitoring** and health checks

## 🏆 Demo Features

Perfect for showcasing:

1. **AI Task Management** - Delegate complex tasks to AI agents
2. **Real-time Dashboard** - Live updates and notifications
3. **Multi-Agent Coordination** - Show agents working together
4. **Professional UI** - Clean, modern interface
5. **Scalable Architecture** - Production-ready backend

## 📄 License

Built for hackathons and learning. See deployment costs and usage limits for Railway and Vercel free tiers.

---

**Ready to deploy?** Run `./deploy.sh` and have your AI chief of staff live in minutes! 🚀