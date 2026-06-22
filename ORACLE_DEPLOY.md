# Deploying to Oracle Cloud Free Tier (Free Forever)

## Architecture
```
Oracle Cloud Free ARM VM (always free)
  └─ Docker Compose
       ├─ MySQL 8.0  (port 3306)
       ├─ FastAPI    (port 8000 → Nginx reverse proxy)
       └─ Telegram Bot
```

---

## Step 1 — Create Oracle Cloud account

1. Go to [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)
2. Click **"Start for free"**
3. Fill in your details (requires credit card for verification, but won't be charged)
4. Verify your email

---

## Step 2 — Create a free VM

1. In Oracle Cloud Console, go to **Compute → Instances → Create Instance**

2. Configure:
   - **Name**: `twi-bot-vm`
   - **Image**: `Canonical Ubuntu 22.04` (ARM, always free eligible)
   - **Shape**: Select **VM.Standard.A1.Flex** (always free)
     - OCPUs: **4**
     - Memory: **24 GB**
   - **Boot volume**: 200 GB (always free)
   - **Networking**: Default VCN, create new public IP

3. Click **Create**

4. Wait ~2 minutes for provisioning

---

## Step 3 — SSH into your VM

```bash
# In Oracle Cloud Console, go to your instance → click the ">" next to SSH
# Or use your own SSH client:
ssh ubuntu@YOUR_VM_PUBLIC_IP
```

The default user for Ubuntu is `ubuntu`.

---

## Step 4 — Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install -y docker-compose git

# Verify
docker --version
docker-compose --version
```

---

## Step 5 — Clone your project

```bash
cd /opt
sudo git clone https://github.com/your-username/twi_bot.git
cd twi_bot
sudo chown -R $USER:$USER .
```

---

## Step 6 — Create `.env` file

```bash
cp .env.docker .env
nano .env
```

Edit with your values:
```env
TELEGRAM_BOT_TOKEN=123456789:AAYourBotTokenFromBotFather
DB_ROOT_PASSWORD=your_strong_root_password
DB_USER=twi_user
DB_PASSWORD=your_strong_user_password
DB_NAME=twi_speech_db
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

## Step 7 — Open firewall ports

```bash
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 3306/tcp   # Optional, only if you need external MySQL access
sudo ufw enable
```

---

## Step 8 — Start Docker Compose

```bash
docker-compose up -d --build
```

Watch the logs:
```bash
docker-compose logs -f
```

Wait until you see:
- MySQL: `ready for connections`
- API: `Uvicorn running on http://0.0.0.0:8000`
- Bot: `Twi speech data collection bot is up and polling`

Press `Ctrl+C` to stop following logs.

---

## Step 9 — Verify it's running

```bash
docker-compose ps
```

All three services should show `State: Up`.

Initialize the database (if empty):
```bash
docker exec -i twi_bot-db-1 mysql -u root -p$DB_ROOT_PASSWORD twi_speech_db < twi_bot/schema.sql
docker exec -i twi_bot-db-1 mysql -u root -p$DB_ROOT_PASSWORD twi_speech_db < twi_bot/migration_add_name.sql
```
(Replace `$DB_ROOT_PASSWORD` with your actual password, or run interactively:)
```bash
docker exec -it twi_bot-db-1 mysql -u root -p
# Then paste the SQL files manually
```

---

## Step 10 — Access your dashboard

Visit in browser:
```
http://YOUR_VM_PUBLIC_IP:8000
```

You should see the Twi Admin dashboard.

---

## Step 11 — (Optional) Add Nginx reverse proxy + HTTPS

**11a. Install Nginx:**
```bash
sudo apt install -y nginx
```

**11b. Create Nginx config:**
```bash
sudo nano /etc/nginx/sites-available/twi-dashboard
```

Paste (replace `yourdomain.com` with your actual domain):
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable it:
```bash
sudo ln -sf /etc/nginx/sites-available/twi-dashboard /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

**11c. Point your domain DNS** to the VM's public IP (A record).

**11d. Add SSL with Certbot:**
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## Step 12 — (Optional) Auto-restart on boot

```bash
sudo nano /etc/systemd/system/twi-dashboard.service
```

Paste:
```ini
[Unit]
Description=Twi Dashboard Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/twi_bot
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable it:
```bash
sudo systemctl daemon-reload
sudo systemctl enable twi-dashboard.service
sudo systemctl start twi-dashboard.service
```

---

## Updating your deployment

```bash
cd /opt/twi_bot
git pull
docker-compose down
docker-compose up -d --build
```

## Quick reference commands

| Task | Command |
|------|---------|
| View logs (all) | `docker-compose logs -f` |
| View API logs | `docker-compose logs -f api` |
| View bot logs | `docker-compose logs -f bot` |
| Restart all | `docker-compose restart` |
| Stop all | `docker-compose stop` |
| Start all | `docker-compose start` |
| Full rebuild | `docker-compose down && docker-compose up -d --build` |
