# FaceMark (FRCAS) - Production Deployment Guide

This guide covers deploying FaceMark across various infrastructure environments:
1. **PaaS Cloud (Render.com / Railway.app / Fly.io)** - 1-Click Git deployment.
2. **Hugging Face Spaces (Docker Space)** - Free cloud CPU container.
3. **Campus / Local Wi-Fi Server** - Self-hosted on college LAN with zero cloud costs.
4. **Linux VPS (Ubuntu / AWS EC2 / DigitalOcean)** - Docker Compose + Nginx HTTPS.

> [!IMPORTANT]
> **Camera HTTPS Security Requirement:** Modern web browsers (especially Chrome, Edge, and iOS Safari) strictly require **`localhost`** or **`https://`** to grant camera permissions (`navigator.mediaDevices.getUserMedia`). For any public domain deployment, SSL/HTTPS is mandatory.

---

## Option 1: PaaS Cloud Deployment (Render.com)

Render allows free and low-cost containerized deployments directly connected to your GitHub repository.

1. Sign in to [Render.com](https://render.com) using your GitHub account (`PavanCodeNexus`).
2. Click **New +** ➔ **Web Service**.
3. Select your repository: `PavanCodeNexus/FRCAS`.
4. Configure service settings:
   * **Name:** `facemark-attendance`
   * **Language / Runtime:** `Docker`
   * **Instance Type:** `Starter` (or Free)
5. Environment Variables:
   * `PORT`: `8000`
   * `INSIGHTFACE_MODEL`: `buffalo_sc`
   * `SECRET_KEY`: *(Generate a secure random string)*
6. Click **Create Web Service**. Render builds the `Dockerfile`, pre-downloads the model, and provisions an automated HTTPS URL (e.g. `https://facemark-attendance.onrender.com`).

---

## Option 2: Railway.app Deployment

1. Go to [Railway.app](https://railway.app) and click **Start a New Project**.
2. Select **Deploy from GitHub repo** ➔ choose `PavanCodeNexus/FRCAS`.
3. Railway automatically detects `Dockerfile`.
4. Under **Settings** ➔ **Networking**, click **Generate Domain** to get a public `*.up.railway.app` HTTPS domain.
5. Add a **Persistent Volume** mounted to `/app/data` to preserve student registrations and SQLite database across restarts.

---

## Option 3: Campus Local Network / College Wi-Fi (Zero Cloud Cost)

For university environments where all classrooms and devices share the same campus Wi-Fi network:

### 1. Launch on the Host Server
Run Uvicorn bound to all network adapters (`0.0.0.0`):

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### 2. Find the Host Local IP
* **Windows:** Run `ipconfig` (Look for IPv4 Address, e.g. `192.168.1.15`).
* **Linux / Mac:** Run `hostname -I` or `ip addr`.

### 3. Access Across Devices
* **Professor Portal:** `http://192.168.1.15:8000/professor`
* **Student Portal:** `http://192.168.1.15:8000/student`

*(Note: Chrome on Android allows camera on private IP ranges; for iOS Safari, see Option 4 for HTTPS).*

---

## Option 4: Linux VPS with Docker Compose & Nginx (Production with SSL)

### 1. Server Setup
SSH into your Ubuntu 22.04 / 24.04 server:

```bash
sudo apt update && sudo apt install -y git docker.io docker-compose-v2 nginx certbot python3-certbot-nginx
```

### 2. Clone and Start FaceMark
```bash
git clone https://github.com/PavanCodeNexus/FRCAS.git
cd FRCAS
docker compose up -d --build
```

### 3. Configure Nginx Reverse Proxy
Create `/etc/nginx/sites-available/facemark`:

```nginx
server {
    server_name attendance.yourcollege.edu;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and obtain a free SSL certificate:

```bash
sudo ln -s /etc/nginx/sites-available/facemark /etc/nginx/sites-enabled/
sudo certbot --nginx -d attendance.yourcollege.edu
sudo systemctl restart nginx
```

## Preventing Render Free Tier Sleep (24/7 Keep-Alive)

On Render's Free Tier, web services automatically **spin down (hibernate) after 15 minutes of inactivity**. The next visitor experiences a 50+ second "cold start" delay while the container reboots.

To keep FaceMark running **24/7 with instant response times (<1s)** at zero cost:

### Solution 1: UptimeRobot (Recommended)
[UptimeRobot](https://uptimerobot.com) is a free monitoring service that sends periodic HTTP requests:

1. Create a free account at [uptimerobot.com](https://uptimerobot.com).
2. Click **+ Add New Monitor**:
   * **Monitor Type:** `HTTP(s)`
   * **Friendly Name:** `FaceMark Render Keep-Alive`
   * **URL (or IP):** `https://<your-service-name>.onrender.com/health`
   * **Monitoring Interval:** `10 minutes` (or `5 minutes`)
3. Click **Create Monitor**.
4. UptimeRobot will ping the `/health` endpoint every 10 minutes, keeping the container perpetually warm and awake.

### Alternative: Cron-Job.org
You can also use [Cron-Job.org](https://cron-job.org) (completely free):
* Set target URL to `https://<your-service-name>.onrender.com/health`
* Set execution schedule to `Every 10 minutes`.

> [!NOTE]
> **Render 750-Hour Free Limit:** Render grants **750 free instance hours per month**. One month (31 days) has $31 \times 24 = 744$ hours. Keeping **one** web service running 24/7 consumes 744 hours, staying completely within your free monthly allowance.

---

## Health Check & Verification

Once deployed, verify the endpoints:
* **Health Check:** `curl -I https://<your-domain>/`
* **PWA Manifest:** `curl https://<your-domain>/manifest.json`
* **Swagger API Docs:** `https://<your-domain>/docs`
