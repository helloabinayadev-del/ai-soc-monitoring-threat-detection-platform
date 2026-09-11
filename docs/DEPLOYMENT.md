# Production Deployment & Installation Guide

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Prerequisites, Local Setup, Environment Configuration, & Docker Compose Setup  
**Date**: August 28, 2026  

---

## 1. Environment Prerequisites

- **Python**: 3.10+ (Tested on Python 3.14)
- **Node.js**: v18+ / npm v9+
- **Docker**: Docker Engine v24+ & Docker Compose v2+

---

## 2. Environment Variables Configuration

Copy `.env.example` to `.env` in `backend/`:

```env
# Application Settings
ENVIRONMENT=production
DEBUG=false
PROJECT_NAME="AI SOC Monitoring Platform"

# Security Configuration
JWT_SECRET=super-secret-jwt-key-change-in-production-2026
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database Configuration
DATABASE_URL=sqlite:///./soc_platform.db

# External Threat Intelligence Feeds (Optional)
THREAT_INTEL_API_KEY=
```

---

## 3. Local Development Setup

### Backend Setup:
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -c "from app.core.database import Base, engine; import app.models; Base.metadata.create_all(bind=engine)"
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

---

## 4. Docker Container Deployment

Run backend and frontend in containerized isolation:

```bash
docker-compose up --build -d
```

### Service Health Verification:
```bash
docker-compose ps
curl http://localhost:8000/api/v1/health/
```

- **Frontend Dashboard**: `http://localhost:5173`
- **Backend API Docs**: `http://localhost:8000/docs`
- **WebSocket Endpoint**: `ws://localhost:8000/ws/soc-stream`
