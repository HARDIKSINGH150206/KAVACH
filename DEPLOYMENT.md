# KAVACH Deployment Guide

This guide covers deploying KAVACH in controlled environments and pilot deployments.

## Prerequisites

- Python 3.12+
- Docker (optional but recommended)
- 4GB+ RAM for model inference
- CUDA-compatible GPU (optional, CPU fallback available)

## Quick Start with Docker

```bash
# Build the container
docker build -t kavach:latest .

# Run with demo mode
docker run -p 8000:8000 kavach:latest

# Access the dashboard at http://localhost:8000
```

## Manual Installation

### 1. Environment Setup

```bash
# Clone and setup
git clone <repository>
cd kavach
python3 -m venv kavach-env
source kavach-env/bin/activate
pip install -r requirements.txt
```

### 2. Model Assets

Download required models:

```bash
python3 scripts/download_models.py
```

### 3. Configuration

Edit `kavach.yml` for your environment:

```yaml
audio_source: mic  # or 'demo' for synthetic audio
fusion:
  audio_weight: 0.55
  sms_weight: 0.45
  transcript_weight: 0.20
logging:
  level: INFO
```

### 4. Start Services

```bash
# Start the backend server
./kavach-env/bin/python -m backend.cli start

# Or run directly
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Production Deployment

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  kavach:
    build: .
    ports:
      - "8000:8000"
    environment:
      - KAVACH_MODE=production
      - KAVACH_AUDIO_SOURCE=mic
    volumes:
      - ./logs:/app/logs
      - ./kavach.yml:/app/kavach.yml:ro
    restart: unless-stopped
```

### Systemd Service

Create `/etc/systemd/system/kavach.service`:

```ini
[Unit]
Description=KAVACH Fraud Detection
After=network.target

[Service]
Type=simple
User=kavach
WorkingDirectory=/opt/kavach
ExecStart=/opt/kavach/kavach-env/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## API Integration

### Scoring Endpoints

```bash
# Score SMS
curl -X POST http://localhost:8000/api/v1/score/sms \
  -H "Content-Type: application/json" \
  -d '{"text": "Your package is ready for delivery"}'

# Score Audio
curl -X POST http://localhost:8000/api/v1/score/audio \
  -H "Content-Type: application/json" \
  -d '{"samples": [0.1, 0.2, ...], "sample_rate": 16000}'

# Fuse Scores
curl -X POST http://localhost:8000/api/v1/score/fusion \
  -H "Content-Type: application/json" \
  -d '{"audio_score": 0.8, "sms_score": 0.6, "transcript_score": 0.3}'
```

### WebSocket Streaming

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/threat');
ws.onmessage = (event) => {
    const threat = JSON.parse(event.data);
    console.log('Threat detected:', threat);
};
```

## Monitoring

### Health Checks

```bash
curl http://localhost:8000/api/v1/health
```

### Logs

Logs are written to `logs/threat_events.jsonl`:

```bash
tail -f logs/threat_events.jsonl
```

### Metrics

Monitor these endpoints:
- `/api/v1/health` - System status and model readiness
- `/api/v1/config` - Current configuration
- WebSocket connections for real-time threats

## Security Considerations

1. **Network Security**
   - Run behind reverse proxy
   - Use HTTPS in production
   - Restrict API access with authentication

2. **Audio Privacy**
   - Audio data is processed locally
   - No audio sent to external services
   - Configure appropriate audio sources

3. **Model Security**
   - Models run locally, no external API calls
   - Validate model integrity on startup
   - Keep models updated

## Troubleshooting

### Common Issues

1. **CUDA Errors**
   ```bash
   # Force CPU mode
   export CUDA_VISIBLE_DEVICES=""
   ```

2. **Port Conflicts**
   ```bash
   # Change port
   uvicorn backend.main:app --port 8080
   ```

3. **Model Loading Failures**
   ```bash
   # Check model assets
   python scripts/download_models.py
   ```

### Performance Tuning

- Use GPU for better inference performance
- Adjust fusion weights based on your use case
- Monitor memory usage with large audio files

## Support

For issues and questions:
- Check logs in `logs/` directory
- Review readiness report at `/api/v1/health`
- Validate configuration in `kavach.yml`
