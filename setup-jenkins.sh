#!/bin/bash

# DocQA-MS Jenkins CI/CD Setup Script
# This script sets up Jenkins with ngrok for automated testing

set -e

echo "🚀 Setting up DocQA-MS Jenkins CI/CD Environment"
echo "================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f ".env.jenkins" ]; then
    echo "📝 Creating environment configuration..."
    cp .env.jenkins.example .env.jenkins
    echo "⚠️  Please edit .env.jenkins with your actual values before continuing."
    echo "   Required: NGROK_AUTH_TOKEN"
    echo "   See .env.jenkins for all configuration options."
    read -p "Press Enter after configuring .env.jenkins..."
fi

# Load environment variables
if [ -f ".env.jenkins" ]; then
    export $(grep -v '^#' .env.jenkins | xargs)
fi

# Validate required environment variables
if [ -z "$NGROK_AUTH_TOKEN" ]; then
    echo "❌ NGROK_AUTH_TOKEN is required. Please set it in .env.jenkins"
    exit 1
fi

echo "🐳 Starting Jenkins and ngrok..."
docker-compose -f docker-compose.jenkins.yml up -d

echo "⏳ Waiting for Jenkins to start..."
sleep 30

# Get Jenkins initial admin password
JENKINS_PASSWORD=$(docker exec docqa-jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "")

if [ -n "$JENKINS_PASSWORD" ]; then
    echo ""
    echo "🔐 Jenkins Initial Setup Required:"
    echo "=================================="
    echo "1. Open Jenkins at: http://localhost:8080"
    echo "2. Use this initial admin password: $JENKINS_PASSWORD"
    echo "3. Install suggested plugins"
    echo "4. Create admin user"
    echo ""
else
    echo "✅ Jenkins is running at: http://localhost:8080"
fi

# Get ngrok URL
echo "⏳ Waiting for ngrok tunnel..."
sleep 10

NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"[^"]*' | grep -o '[^"]*$' || echo "")

if [ -n "$NGROK_URL" ]; then
    echo ""
    echo "🌐 ngrok Tunnel Active:"
    echo "======================"
    echo "Jenkins Webhook URL: ${NGROK_URL}"
    echo "Use this URL in GitHub webhook configuration"
    echo ""
else
    echo "⚠️  ngrok tunnel not ready yet. Check status at: http://localhost:4040"
fi

echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. Complete Jenkins setup in browser"
echo "2. Install required plugins: Git, Docker, Pipeline"
echo "3. Configure GitHub webhook:"
echo "   - Go to your GitHub repo → Settings → Webhooks"
echo "   - Add webhook with URL: ${NGROK_URL}/github-webhook/"
echo "   - Content type: application/json"
echo "   - Events: Push, Pull Request"
echo "4. Create Jenkins pipeline job:"
echo "   - New Item → Pipeline"
echo "   - Name: docqa-ms-pipeline"
echo "   - Pipeline from SCM → Git"
echo "   - Repository URL: https://github.com/YOUR_USERNAME/YOUR_REPO"
echo "   - Script Path: Jenkinsfile"
echo "5. Run initial build to test setup"

echo ""
echo "🔧 Useful Commands:"
echo "=================="
echo "# Check Jenkins status:"
echo "docker-compose -f docker-compose.jenkins.yml ps"
echo ""
echo "# View Jenkins logs:"
echo "docker-compose -f docker-compose.jenkins.yml logs -f jenkins"
echo ""
echo "# View ngrok logs:"
echo "docker-compose -f docker-compose.jenkins.yml logs -f ngrok"
echo ""
echo "# Stop services:"
echo "docker-compose -f docker-compose.jenkins.yml down"
echo ""
echo "# Restart services:"
echo "docker-compose -f docker-compose.jenkins.yml restart"

echo ""
echo "✅ Setup complete! Jenkins is ready for CI/CD pipelines."