# 🚀 Deployment Guide

Complete guide to deploying BARD-RECO to production.

## 📋 Pre-Deployment Checklist

- [ ] Change default admin password
- [ ] Configure environment variables
- [ ] Set up proper authentication
- [ ] Configure HTTPS/SSL
- [ ] Set file upload limits
- [ ] Enable logging
- [ ] Configure backup strategy

## 1️⃣ Streamlit Cloud (Easiest - FREE)

### Advantages
- ✅ 100% Free tier available
- ✅ No server management
- ✅ Automatic HTTPS
- ✅ GitHub integration
- ✅ 1-click deployment

### Steps

1. **Prepare Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/bard-reco.git
   git push -u origin main
   ```

2. **Deploy**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Main file: `app.py`
   - Click "Deploy"

3. **Configure Secrets** (Optional)
   - In Streamlit Cloud dashboard
   - Go to App settings → Secrets
   - Add any sensitive configuration

4. **Share**
   - Your app URL: `https://your-username-bard-reco.streamlit.app`
   - Share with users!

### Limitations
- 1 GB RAM limit
- Limited CPU
- Public by default (can be private with password)

---

## 2️⃣ Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed

### Steps

1. **Build and Run**
   ```bash
   cd streamlit-app
   docker-compose up -d
   ```

2. **Access**
   - Open http://localhost:8501

3. **Stop**
   ```bash
   docker-compose down
   ```

### Production Docker Setup

1. **Use Environment Variables**

   Create `.env` file:
   ```env
   STREAMLIT_SERVER_PORT=8501
   STREAMLIT_SERVER_ADDRESS=0.0.0.0
   STREAMLIT_SERVER_HEADLESS=true
   ```

2. **Configure Nginx Reverse Proxy**

   `/etc/nginx/sites-available/bard-reco`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable HTTPS with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

---

## 3️⃣ AWS Deployment

### Option A: AWS EC2

1. **Launch EC2 Instance**
   - Amazon Linux 2 or Ubuntu 20.04
   - t2.medium or larger
   - Configure security group (port 8501)

2. **Connect and Install**
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip

   # Update system
   sudo yum update -y  # Amazon Linux
   # OR
   sudo apt update && sudo apt upgrade -y  # Ubuntu

   # Install Python 3.11
   sudo yum install python311 -y  # Amazon Linux
   # OR
   sudo apt install python3.11 python3.11-venv -y  # Ubuntu

   # Install Docker
   sudo yum install docker -y
   sudo service docker start
   sudo usermod -a -G docker ec2-user

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Deploy Application**
   ```bash
   git clone https://github.com/YOUR_USERNAME/bard-reco.git
   cd bard-reco/streamlit-app
   docker-compose up -d
   ```

4. **Configure Auto-Start**
   ```bash
   # Create systemd service
   sudo nano /etc/systemd/system/bard-reco.service
   ```

   Add:
   ```ini
   [Unit]
   Description=BARD-RECO Streamlit App
   After=docker.service
   Requires=docker.service

   [Service]
   Type=oneshot
   RemainAfterExit=yes
   WorkingDirectory=/home/ec2-user/bard-reco/streamlit-app
   ExecStart=/usr/local/bin/docker-compose up -d
   ExecStop=/usr/local/bin/docker-compose down

   [Install]
   WantedBy=multi-user.target
   ```

   Enable:
   ```bash
   sudo systemctl enable bard-reco
   sudo systemctl start bard-reco
   ```

### Option B: AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize**
   ```bash
   cd streamlit-app
   eb init -p docker bard-reco
   ```

3. **Create Environment**
   ```bash
   eb create production-env
   ```

4. **Deploy**
   ```bash
   eb deploy
   ```

### Option C: AWS ECS/Fargate

1. **Push to ECR**
   ```bash
   aws ecr create-repository --repository-name bard-reco
   docker build -t bard-reco .
   docker tag bard-reco:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/bard-reco:latest
   docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/bard-reco:latest
   ```

2. **Create ECS Service**
   - Use AWS Console or CLI
   - Configure task definition
   - Set up load balancer
   - Deploy

---

## 4️⃣ Azure Deployment

### Azure App Service

1. **Login to Azure**
   ```bash
   az login
   ```

2. **Create Resource Group**
   ```bash
   az group create --name bard-reco-rg --location eastus
   ```

3. **Create App Service Plan**
   ```bash
   az appservice plan create \
     --name bard-reco-plan \
     --resource-group bard-reco-rg \
     --sku B1 \
     --is-linux
   ```

4. **Create Web App**
   ```bash
   az webapp create \
     --resource-group bard-reco-rg \
     --plan bard-reco-plan \
     --name bard-reco-app \
     --runtime "PYTHON:3.11"
   ```

5. **Deploy from GitHub**
   ```bash
   az webapp deployment source config \
     --name bard-reco-app \
     --resource-group bard-reco-rg \
     --repo-url https://github.com/YOUR_USERNAME/bard-reco \
     --branch main \
     --manual-integration
   ```

---

## 5️⃣ Google Cloud Platform

### Cloud Run

1. **Enable APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. **Build and Push**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT/bard-reco
   ```

3. **Deploy**
   ```bash
   gcloud run deploy bard-reco \
     --image gcr.io/YOUR_PROJECT/bard-reco \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

---

## 6️⃣ Heroku

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login**
   ```bash
   heroku login
   ```

3. **Create App**
   ```bash
   heroku create bard-reco-app
   ```

4. **Add Procfile**
   ```bash
   echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

---

## 🔒 Security Best Practices

### 1. Environment Variables
Never hardcode secrets. Use environment variables:

```python
import os
SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-key')
```

### 2. HTTPS/SSL
Always use HTTPS in production:
- Streamlit Cloud: Automatic
- AWS: Use CloudFront or ALB with ACM certificate
- Other: Use Let's Encrypt with Nginx

### 3. Authentication
- Change default passwords immediately
- Implement rate limiting
- Use strong password policies
- Consider OAuth/SAML for enterprise

### 4. File Upload Security
```python
# Limit file sizes
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

# Validate file types
ALLOWED_EXTENSIONS = ['.xlsx', '.xls', '.csv']

# Scan for malware (optional)
# Use ClamAV or similar
```

### 5. Database Security
For production, replace JSON files with database:
- PostgreSQL
- MySQL
- MongoDB
- Use connection pooling
- Encrypt sensitive data

---

## 📊 Monitoring

### Application Monitoring

1. **Streamlit Cloud**
   - Built-in logs
   - Resource usage dashboard

2. **Self-Hosted**
   Install monitoring tools:

   ```bash
   # Prometheus + Grafana
   docker run -d \
     --name prometheus \
     -p 9090:9090 \
     prom/prometheus

   docker run -d \
     --name grafana \
     -p 3000:3000 \
     grafana/grafana
   ```

### Error Tracking

```python
# Add to app.py
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0
)
```

---

## 💾 Backup Strategy

### Data Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz data/
aws s3 cp backup_$DATE.tar.gz s3://your-bucket/backups/
```

### Database Backup

```bash
# PostgreSQL
pg_dump -U username database > backup.sql

# MongoDB
mongodump --out /backup/path
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Deploy to Streamlit Cloud
        run: |
          # Streamlit Cloud auto-deploys on push

      # OR Deploy to AWS
      - name: Deploy to AWS
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster my-cluster --service bard-reco --force-new-deployment
```

---

## 📞 Support

For deployment issues:
- Check logs: `docker-compose logs`
- Streamlit docs: https://docs.streamlit.io
- Open GitHub issue

---

## ✅ Post-Deployment

After deployment:

1. [ ] Test all functionality
2. [ ] Verify user authentication
3. [ ] Test file uploads
4. [ ] Run sample reconciliation
5. [ ] Check exports/reports
6. [ ] Monitor performance
7. [ ] Set up automated backups
8. [ ] Document user credentials
9. [ ] Share access link with users

---

**Congratulations! Your BARD-RECO system is now live! 🎉**
