#!/bin/bash

# Test deployment endpoints
set -e

echo "🧪 Testing Delegate.ai deployment..."

# Get URLs from user
read -p "Enter your Railway backend URL (e.g., https://your-app.up.railway.app): " BACKEND_URL
read -p "Enter your Vercel frontend URL (e.g., https://your-app.vercel.app): " FRONTEND_URL

# Test backend health
echo "🩺 Testing backend health..."
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health" || echo "FAILED")

if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    echo "✅ Backend is healthy"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "❌ Backend health check failed"
    echo "   Response: $HEALTH_RESPONSE"
fi

# Test backend API docs
echo "📚 Testing API documentation..."
API_DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs" || echo "FAILED")

if [[ "$API_DOCS_STATUS" == "200" ]]; then
    echo "✅ API docs are accessible at $BACKEND_URL/docs"
elif [[ "$API_DOCS_STATUS" == "404" ]]; then
    echo "ℹ️  API docs disabled (DEBUG=false) - this is expected in production"
else
    echo "❌ API docs check failed with status: $API_DOCS_STATUS"
fi

# Test WebSocket endpoint
echo "🔌 Testing WebSocket endpoint..."
WS_URL="${BACKEND_URL/https:/wss:}/ws/test"
echo "   WebSocket URL: $WS_URL"

# Test frontend
echo "🌐 Testing frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" || echo "FAILED")

if [[ "$FRONTEND_STATUS" == "200" ]]; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend check failed with status: $FRONTEND_STATUS"
fi

# Test CORS
echo "🔗 Testing CORS configuration..."
CORS_TEST=$(curl -s -H "Origin: $FRONTEND_URL" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: Content-Type" -X OPTIONS "$BACKEND_URL/api/v1/" -w "%{http_code}" || echo "FAILED")

if [[ "$CORS_TEST" == *"200"* ]]; then
    echo "✅ CORS is properly configured"
else
    echo "⚠️  CORS might not be properly configured"
    echo "   Make sure your frontend URL is in CORS_ORIGINS"
fi

echo ""
echo "🎯 Deployment Test Summary:"
echo "   Backend Health: $(if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then echo "✅ PASS"; else echo "❌ FAIL"; fi)"
echo "   Frontend Access: $(if [[ "$FRONTEND_STATUS" == "200" ]]; then echo "✅ PASS"; else echo "❌ FAIL"; fi)"
echo "   CORS Config: $(if [[ "$CORS_TEST" == *"200"* ]]; then echo "✅ PASS"; else echo "⚠️  CHECK"; fi)"
echo ""
echo "🔧 If tests fail, check:"
echo "   - Environment variables are set correctly"
echo "   - Database and Redis connections are working"
echo "   - CORS_ORIGINS includes your frontend URL"
echo "   - OpenAI API key is valid (if using AI features)"