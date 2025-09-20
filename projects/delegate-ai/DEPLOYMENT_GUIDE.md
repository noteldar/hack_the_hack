# Delegate.ai Deployment Guide

This guide will help you deploy the Delegate.ai hackathon project to free cloud platforms.

## Architecture Overview

- **Backend**: FastAPI application (Railway)
- **Frontend**: Next.js 14 application (Vercel)
- **Database**: PostgreSQL (Railway)
- **Cache/Queue**: Redis (Railway)
- **AI System**: OpenAI API integration

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **Vercel Account**: Sign up at https://vercel.com
3. **OpenAI API Key**: Get from https://platform.openai.com
4. **OAuth Credentials**: Google/Microsoft OAuth apps (optional)

## Step 1: Deploy Backend to Railway

### 1.1 Install Railway CLI

```bash
curl -fsSL https://railway.app/install.sh | sh
```

### 1.2 Login and Initialize

```bash
cd projects/delegate-ai/backend
railway login
railway init
```

### 1.3 Add PostgreSQL Database

```bash
railway add postgresql
```

### 1.4 Add Redis Cache

```bash
railway add redis
```

### 1.5 Set Environment Variables

Go to your Railway dashboard and set these environment variables:

**Required:**
```env
# Database (automatically set by Railway PostgreSQL addon)
DATABASE_URL=postgresql+asyncpg://...

# Redis (automatically set by Railway Redis addon)
REDIS_URL=redis://...

# Security
SECRET_KEY=generate_secure_random_key_here
DEBUG=false

# CORS (update with your Vercel domain)
CORS_ORIGINS=["https://your-app.vercel.app", "http://localhost:3000"]

# OpenAI
OPENAI_API_KEY=your_openai_api_key
```

**Optional (for OAuth):**
```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
```

### 1.6 Deploy

```bash
railway up
```

Your backend will be available at: `https://your-project.up.railway.app`

## Step 2: Deploy Frontend to Vercel

### 2.1 Install Vercel CLI

```bash
npm install -g vercel
```

### 2.2 Deploy

```bash
cd projects/delegate-ai/frontend
vercel
```

Follow the prompts:
- Link to existing project? **N**
- What's your project's name? **delegate-ai-frontend**
- In which directory is your code located? **.**

### 2.3 Set Environment Variables

In your Vercel dashboard, go to Settings > Environment Variables and add:

```env
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend.up.railway.app
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id (optional)
NEXT_PUBLIC_MICROSOFT_CLIENT_ID=your_microsoft_client_id (optional)
```

### 2.4 Redeploy with Environment Variables

```bash
vercel --prod
```

Your frontend will be available at: `https://your-app.vercel.app`

## Step 3: Update CORS Settings

After deploying the frontend, update the CORS settings in Railway:

1. Go to Railway dashboard > Your Project > Variables
2. Update `CORS_ORIGINS` to include your Vercel URL:
   ```
   ["https://your-app.vercel.app", "http://localhost:3000"]
   ```

## Step 4: Database Setup

The database will be automatically initialized with Alembic migrations when the backend starts.

If you need to manually run migrations:

```bash
railway run alembic upgrade head
```

## Step 5: Testing the Deployment

### Backend Health Check

Visit: `https://your-backend.up.railway.app/health`

Expected response:
```json
{
  "status": "healthy",
  "redis": "healthy",
  "version": "1.0.0"
}
```

### API Documentation

Visit: `https://your-backend.up.railway.app/docs` (if DEBUG=true)

### Frontend Application

Visit: `https://your-app.vercel.app`

## Troubleshooting

### Backend Issues

1. **Database Connection**: Check DATABASE_URL format in Railway
2. **Redis Connection**: Ensure Redis addon is properly connected
3. **Migration Errors**: Check Railway logs and run migrations manually
4. **CORS Errors**: Verify CORS_ORIGINS includes your frontend domain

### Frontend Issues

1. **API Connection**: Verify NEXT_PUBLIC_API_URL points to your Railway backend
2. **WebSocket Issues**: Check NEXT_PUBLIC_WS_URL and ensure it uses wss://
3. **Build Errors**: Check Vercel build logs for missing dependencies

### Common Commands

```bash
# Railway
railway logs                 # View backend logs
railway run bash            # Access backend shell
railway status              # Check service status

# Vercel
vercel logs                 # View frontend logs
vercel dev                  # Local development
vercel --prod              # Production deployment
```

## Environment Variables Summary

### Backend (Railway)
- `DATABASE_URL` - PostgreSQL connection (auto-set)
- `REDIS_URL` - Redis connection (auto-set)
- `SECRET_KEY` - JWT secret key
- `OPENAI_API_KEY` - OpenAI API key
- `CORS_ORIGINS` - Frontend origins
- `DEBUG` - Set to false for production

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL` - Backend API endpoint
- `NEXT_PUBLIC_WS_URL` - WebSocket endpoint
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID` - OAuth (optional)
- `NEXT_PUBLIC_MICROSOFT_CLIENT_ID` - OAuth (optional)

## Live URLs

After successful deployment:

- **Backend API**: `https://your-project.up.railway.app`
- **Frontend App**: `https://your-app.vercel.app`
- **API Docs**: `https://your-project.up.railway.app/docs`
- **Health Check**: `https://your-project.up.railway.app/health`

## Features Enabled

✅ FastAPI backend with async support
✅ PostgreSQL database with migrations
✅ Redis caching and background jobs
✅ WebSocket real-time updates
✅ OAuth authentication (Google/Microsoft)
✅ OpenAI API integration
✅ Professional Next.js frontend
✅ Real-time dashboard updates
✅ CORS configuration for secure communication

## Support

For deployment issues:
- Check Railway logs: `railway logs`
- Check Vercel logs in dashboard
- Verify environment variables are set correctly
- Test API endpoints manually

The application should now be fully functional for your hackathon demo!