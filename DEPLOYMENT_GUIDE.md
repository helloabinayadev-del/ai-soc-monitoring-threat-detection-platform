# Deployment & Production Setup Guide

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Prerequisites, Local Setup, Docker Compose, & Production Configuration  

---

## 1. Prerequisites

- **Python**: 3.10+ (Tested on Python 3.14)
- **Node.js**: v18+ / npm v9+
- **Docker**: Docker Engine v24+ & Docker Compose v2+

---

## 2. Local Environment Setup

### 2.1 Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m pytest
uvicorn app.main:app --reload --port 8000
```

### 2.2 Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 3. Docker Container Deployment

```bash
docker-compose up --build -d
docker-compose ps
```

- **Backend REST API & OpenAPI Docs**: `http://localhost:8000/docs`
- **Frontend SOC Dashboard**: `http://localhost:5173`
- **WebSocket Real-Time Stream**: `ws://localhost:8000/ws/soc-stream`
