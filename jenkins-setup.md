# Simple Jenkins CI/CD Setup for DocQA-MS

This guide shows how to set up basic Jenkins CI/CD that tests every commit push using ngrok.

## What You Need

1. **Jenkins Server** - Can run locally or on a server
2. **ngrok account** - For exposing Jenkins to GitHub webhooks
3. **GitHub repository** - Your DocQA-MS code

## Step 1: Install Jenkins

### Option A: Run Jenkins Locally with Docker

```bash
# Run Jenkins in Docker
docker run -d -p 8080:8080 -p 50000:50000 --name jenkins \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts

# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Option B: Install Jenkins Directly

Follow the official Jenkins installation guide for your OS.

## Step 2: Setup ngrok

1. **Install ngrok:**
   ```bash
   # Download from https://ngrok.com/download
   # Or using npm: npm install -g ngrok
   ```

2. **Login to ngrok:**
   ```bash
   ngrok authtoken YOUR_NGROK_AUTH_TOKEN
   ```

3. **Start ngrok tunnel for Jenkins:**
   ```bash
   ngrok http 8080
   ```

   This gives you a URL like: `https://abc123.ngrok.io`

## Step 3: Configure Jenkins

1. **Access Jenkins:**
   - Open: http://localhost:8080
   - Use the initial admin password

2. **Install Plugins:**
   - Go to: Manage Jenkins → Manage Plugins
   - Install: Git, Docker, Pipeline

3. **Create Pipeline Job:**
   - Click: New Item
   - Name: `docqa-ms-ci`
   - Type: Pipeline
   - Click OK

4. **Configure Pipeline:**
   ```
   Definition: Pipeline script from SCM
   SCM: Git
   Repository URL: https://github.com/YOUR_USERNAME/docqa-ms
   Branch: */main
   Script Path: Jenkinsfile
   ```

5. **Setup Build Triggers:**
   - Check: "GitHub hook trigger for GITScm polling"

## Step 4: Configure GitHub Webhook

1. **Go to GitHub Repository:**
   - Settings → Webhooks → Add webhook

2. **Webhook Settings:**
   ```
   Payload URL: https://YOUR_NGROK_URL.ngrok.io/github-webhook/
   Content type: application/json
   Events: Just the push event
   ```

3. **Test Webhook:**
   - Click "Test" button in GitHub
   - Should trigger Jenkins build

## Step 5: Test the Setup

1. **Make a small change** to any file in your repo
2. **Commit and push** to GitHub
3. **Check Jenkins** - should automatically start a build
4. **Monitor the build** in Jenkins dashboard

## What the Pipeline Does

The `Jenkinsfile` will:

1. **Checkout Code** - Get latest code from GitHub
2. **Test Backend** - Basic import tests for all services (including ML service)
3. **Test Frontend** - Build the React app
4. **Build Docker Images** - Create containers for all services
5. **Deploy** - Ready for deployment (when on main branch)

## Services Tested

The pipeline tests all your microservices:
- api_gateway
- doc_ingestor
- deid
- indexer_semantique
- llm_qa
- synthese_comparative
- audit_logger
- **ml_service** (included!)

## Troubleshooting

### Jenkins Not Starting
```bash
# Check if port 8080 is free
netstat -an | find "8080"

# Kill any process using port 8080
# Then restart Jenkins
```

### ngrok Issues
```bash
# Check ngrok status
curl http://localhost:4040/api/tunnels

# Restart ngrok
ngrok http 8080
```

### Webhook Not Working
- Check the ngrok URL is correct
- Verify Jenkins is running
- Check GitHub webhook delivery logs
- Make sure "GitHub hook trigger" is enabled in Jenkins

### Build Failures
- Check Jenkins build console output
- Make sure Docker is installed and running
- Verify all required files exist in the repository

## Next Steps

Once basic CI/CD is working, you can add:
- More comprehensive tests
- Security scanning
- Deployment to staging/production
- Notifications (Slack, email)
- Code coverage reports

## Cost

- **Jenkins**: Free (open source)
- **ngrok**: Free tier allows 1 tunnel, good for basic CI/CD
- **GitHub**: Free for public repos

That's it! Now every commit push will automatically trigger testing in Jenkins.