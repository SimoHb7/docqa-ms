# DocQA-MS Jenkins CI/CD Setup Guide

This guide provides complete instructions for setting up Jenkins with ngrok for automated testing on every commit push.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [GitHub Integration](#github-integration)
5. [Pipeline Configuration](#pipeline-configuration)
6. [Testing Strategy](#testing-strategy)
7. [Deployment Strategy](#deployment-strategy)
8. [Monitoring & Notifications](#monitoring--notifications)
9. [Troubleshooting](#troubleshooting)
10. [Security Considerations](#security-considerations)

## 🔧 Prerequisites

### Required Software
- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **Git** (2.30+)
- **curl** and **wget** for downloading tools

### Required Accounts
- **ngrok account** (free tier available)
- **GitHub account** with repository access
- **Auth0 account** (for authentication)
- **Groq API account** (for LLM services)

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk Space**: 10GB+ free space
- **Network**: Stable internet connection

## 🚀 Quick Start

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd docqa-ms
   ```

2. **Configure environment:**
   ```bash
   cp .env.jenkins.example .env.jenkins
   # Edit .env.jenkins with your values
   ```

3. **Run setup script:**
   ```bash
   chmod +x setup-jenkins.sh
   ./setup-jenkins.sh
   ```

4. **Complete Jenkins setup in browser:**
   - Open http://localhost:8080
   - Use provided admin password
   - Install suggested plugins
   - Create admin user

5. **Configure GitHub webhook:**
   - Go to GitHub repo → Settings → Webhooks
   - Add webhook URL from ngrok
   - Set events: Push, Pull Request

## 📝 Detailed Setup

### Step 1: Environment Configuration

Create `.env.jenkins` from the example:

```bash
cp .env.jenkins.example .env.jenkins
```

**Required Variables:**
```env
# ngrok (Required)
NGROK_AUTH_TOKEN=your_ngrok_token

# Database (Required for tests)
POSTGRES_PASSWORD=secure_password

# API Keys (Required)
GROQ_API_KEY=your_groq_key
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret

# Optional (for deployment)
RAILWAY_TOKEN=your_railway_token
VERCEL_TOKEN=your_vercel_token
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

### Step 2: Jenkins & ngrok Setup

```bash
# Make script executable
chmod +x setup-jenkins.sh

# Run setup
./setup-jenkins.sh
```

This will:
- Start Jenkins container
- Start ngrok tunnel
- Display setup instructions

### Step 3: Jenkins Initial Configuration

1. **Access Jenkins:**
   - URL: http://localhost:8080
   - Initial password: (shown in terminal)

2. **Install Plugins:**
   - Git
   - Docker
   - Docker Pipeline
   - Pipeline
   - GitHub Integration
   - Slack Notification (optional)

3. **Create Admin User:**
   - Username: admin (or your choice)
   - Password: secure password
   - Full name & email: your details

## 🔗 GitHub Integration

### Webhook Configuration

1. **Go to GitHub Repository:**
   - Settings → Webhooks → Add webhook

2. **Webhook Settings:**
   ```
   Payload URL: https://your-ngrok-url.ngrok.io/github-webhook/
   Content type: application/json
   Secret: (leave empty for now)
   Events: Push, Pull Request
   ```

3. **Test Webhook:**
   - Click "Test" in GitHub
   - Check Jenkins logs for incoming requests

### Jenkins Job Configuration

1. **Create New Pipeline Job:**
   - New Item → Pipeline
   - Name: `docqa-ms-pipeline`

2. **Pipeline Configuration:**
   ```
   Definition: Pipeline script from SCM
   SCM: Git
   Repository URL: https://github.com/YOUR_USERNAME/YOUR_REPO
   Branch: */main
   Script Path: Jenkinsfile
   ```

3. **Build Triggers:**
   - ✅ GitHub hook trigger for GITScm polling

## 🔄 Pipeline Configuration

### Pipeline Stages Overview

The `Jenkinsfile` includes these stages:

1. **Checkout** - Code checkout
2. **Setup Environment** - Install dependencies
3. **Backend Tests** - Unit & integration tests
4. **Frontend Tests** - Lint, type check, unit tests
5. **Security Scan** - Vulnerability checks
6. **Build Docker Images** - Container builds
7. **Integration Tests** - Full system tests
8. **Deploy to Staging** - Staging deployment
9. **Deploy to Production** - Production deployment

### Conditional Execution

- **Backend tests** run when `backend/` files change
- **Frontend tests** run when `InterfaceClinique/` files change
- **Staging deployment** runs on `develop` branch
- **Production deployment** runs on `main` branch

### Parallel Execution

Some stages run in parallel for faster builds:
- Backend and Frontend tests run simultaneously
- Docker image builds run in parallel

## 🧪 Testing Strategy

### Unit Tests
- **Backend**: pytest with coverage reporting
- **Frontend**: Vitest with coverage
- **Coverage threshold**: 80% minimum

### Integration Tests
- **API Gateway**: Endpoint testing
- **Service Communication**: Inter-service calls
- **Database**: Connection and queries
- **Message Queue**: RabbitMQ integration

### End-to-End Tests
- **Frontend**: Playwright/Cypress tests
- **API**: Full request flows
- **ngrok**: Public URL testing

### Security Tests
- **Dependencies**: Safety checks
- **Code**: Bandit security linting
- **Containers**: Docker image scanning

## 🚀 Deployment Strategy

### Staging Environment
- **Trigger**: Push to `develop` branch
- **Environment**: Local Docker containers
- **URL**: localhost:3000 (frontend), localhost:8000 (API)
- **Purpose**: Pre-production testing

### Production Environment
- **Trigger**: Push to `main` branch
- **Environment**: Railway (backend) + Vercel (frontend)
- **URL**: your-app.railway.app + your-app.vercel.app
- **Purpose**: Live production system

### Rollback Strategy
- **Automatic**: Failed deployments don't proceed
- **Manual**: Use Railway/Vercel rollback features
- **Monitoring**: Health checks and alerts

## 📊 Monitoring & Notifications

### Jenkins Built-in Monitoring
- **Build History**: Success/failure tracking
- **Test Results**: Trend analysis
- **Coverage Reports**: Code coverage over time
- **Artifact Storage**: Test reports and logs

### External Notifications
- **Slack Integration**: Build status notifications
- **Email**: Failure alerts
- **GitHub Status**: Commit status updates

### Health Checks
- **Application**: /health endpoints
- **Database**: Connection tests
- **Services**: Inter-service communication
- **External APIs**: Auth0, Groq API status

## 🔧 Troubleshooting

### Common Issues

#### Jenkins Won't Start
```bash
# Check Docker containers
docker-compose -f docker-compose.jenkins.yml ps

# View Jenkins logs
docker-compose -f docker-compose.jenkins.yml logs jenkins

# Restart services
docker-compose -f docker-compose.jenkins.yml restart
```

#### ngrok Tunnel Issues
```bash
# Check ngrok status
curl http://localhost:4040/api/tunnels

# Restart ngrok
docker-compose -f docker-compose.jenkins.yml restart ngrok

# Check ngrok logs
docker-compose -f docker-compose.jenkins.yml logs ngrok
```

#### GitHub Webhook Not Triggering
- Verify ngrok URL is correct
- Check GitHub webhook delivery logs
- Ensure Jenkins is running and webhook endpoint is accessible
- Test webhook manually from GitHub

#### Build Failures
```bash
# Check Jenkins build logs
# Go to Jenkins job → Build History → Console Output

# Run tests locally
docker-compose -f docker-compose.test.yml up -d
pytest backend/ -v

# Check Docker image builds
docker build -t test backend/api_gateway
```

#### Database Connection Issues
```bash
# Test database connection
docker-compose -f docker-compose.test.yml exec postgres-test pg_isready -U testuser -d test_db

# Check database logs
docker-compose -f docker-compose.test.yml logs postgres-test
```

### Performance Optimization

#### Speed Up Builds
- **Caching**: Use Docker layer caching
- **Parallel**: Run tests in parallel
- **Selective**: Only run affected service tests
- **Artifacts**: Cache dependencies between builds

#### Resource Usage
- **Memory**: Increase Docker memory limits
- **CPU**: Allocate more CPU cores
- **Disk**: Clean up old Docker images regularly

## 🔒 Security Considerations

### Jenkins Security
- **Admin Access**: Use strong passwords
- **Plugins**: Keep plugins updated
- **Network**: Restrict Jenkins access if needed
- **Secrets**: Use Jenkins credentials store

### ngrok Security
- **Authentication**: Use ngrok auth token
- **Reserved Domains**: Consider paid plan for custom domains
- **Access Control**: Limit webhook access

### Code Security
- **Secrets**: Never commit secrets to code
- **Dependencies**: Regular security audits
- **Vulnerabilities**: Automated scanning
- **Access Control**: Proper authentication/authorization

### Network Security
- **HTTPS**: Use HTTPS for all external communications
- **Firewalls**: Configure appropriate firewall rules
- **VPN**: Consider VPN for sensitive deployments

## 📈 Scaling & Maintenance

### Scaling Jenkins
- **Multiple Agents**: Add Jenkins agent nodes
- **Load Balancing**: Distribute builds across agents
- **Resource Pools**: Separate resource pools for different build types

### Maintenance Tasks
- **Regular Updates**: Keep Jenkins and plugins updated
- **Log Rotation**: Configure log rotation
- **Backup**: Backup Jenkins configuration
- **Cleanup**: Remove old builds and artifacts

### Monitoring
- **System Resources**: Monitor CPU, memory, disk usage
- **Build Metrics**: Track build success rates and duration
- **Error Patterns**: Identify common failure patterns
- **Performance**: Monitor build times and resource usage

## 🎯 Best Practices

### Pipeline Best Practices
- **Idempotent**: Builds should be reproducible
- **Fast Feedback**: Fail fast on critical issues
- **Clear Stages**: Well-defined pipeline stages
- **Error Handling**: Proper error handling and cleanup

### Code Quality
- **Testing**: Comprehensive test coverage
- **Linting**: Code style consistency
- **Security**: Regular security scans
- **Documentation**: Keep documentation updated

### Deployment Best Practices
- **Blue-Green**: Consider blue-green deployments
- **Canary**: Gradual rollout for major changes
- **Rollback**: Easy rollback procedures
- **Monitoring**: Comprehensive monitoring and alerting

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Jenkins and Docker logs
3. Check GitHub webhook delivery status
4. Verify all environment variables are set correctly

## 📝 Changelog

- **v1.0.0**: Initial Jenkins CI/CD setup with ngrok integration
- Comprehensive testing pipeline
- Staging and production deployment
- Security scanning and monitoring

---

*This setup provides a complete CI/CD solution for the DocQA-MS project with automated testing on every commit.*