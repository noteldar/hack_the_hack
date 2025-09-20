#!/bin/bash

set -e

echo "🚀 Deploying Delegate.ai to Railway and Vercel..."

# Check if required CLIs are installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    curl -fsSL https://railway.app/install.sh | sh
fi

if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Deploy Backend to Railway
echo "📦 Deploying backend to Railway..."
cd backend

# Check if Railway is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

# Initialize project if not exists
if [ ! -f railway.toml ]; then
    echo "🎯 Initializing Railway project..."
    railway init
fi

# Add services if not exists
echo "🗄️ Setting up database and Redis..."
railway add postgresql --yes || echo "PostgreSQL already added"
railway add redis --yes || echo "Redis already added"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

# Get Railway URL
RAILWAY_URL=$(railway status --json | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
echo "✅ Backend deployed to: $RAILWAY_URL"

# Deploy Frontend to Vercel
echo "🌐 Deploying frontend to Vercel..."
cd ../frontend

# Set environment variables
echo "⚙️ Setting up environment variables..."
vercel env add NEXT_PUBLIC_API_URL production <<< "$RAILWAY_URL"
vercel env add NEXT_PUBLIC_WS_URL production <<< "${RAILWAY_URL/https:/wss:}"

# Deploy
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo ""
echo "🔗 Your application URLs:"
echo "   Backend:  $RAILWAY_URL"
echo "   Frontend: https://your-app.vercel.app"
echo ""
echo "📖 Next steps:"
echo "   1. Update CORS_ORIGINS in Railway with your Vercel URL"
echo "   2. Set your OpenAI API key in Railway environment variables"
echo "   3. Test the deployment at your Vercel URL"
echo ""
echo "📚 Full deployment guide: ./DEPLOYMENT_GUIDE.md"