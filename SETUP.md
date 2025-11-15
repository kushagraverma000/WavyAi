# WavyAI Setup Guide

This guide will help you set up and run the WavyAI application.

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- PostgreSQL 15+ with PostGIS and TimescaleDB (if running locally)
- Redis (if running locally)
- Qdrant (if running locally)

## Quick Start with Docker

1. **Clone the repository:**
```bash
git clone <repository-url>
cd WavyAI
```

2. **Copy environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Start services:**
```bash
docker-compose up -d
```

4. **Initialize the database:**
```bash
docker-compose exec backend python scripts/init_db.py
docker-compose exec backend python scripts/load_sample_data.py
```

5. **Place ARGO NetCDF files (optional, for full dataset):**
   - Create directories under `data/raw/<year>/<month>/<day>/`
   - Drop NetCDF files for that day into the folder
   - Example: `data/raw/2016/09/12/argo_profiles_20160912.nc`

The ingestion service recursively scans `data/raw/` and loads any new files it finds.

5. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Local Development Setup

### Backend

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database:**
```bash
python scripts/init_db.py
python scripts/load_sample_data.py
```

6. **Run the backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the frontend:**
```bash
npm run dev
```

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://wavyai:wavyai_password@localhost:5432/wavyai

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector Database
QDRANT_URL=http://localhost:6333

# LLM APIs
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Mapbox
MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_MAPBOX_TOKEN=your_mapbox_token_here
```

## Database Schema

The database schema includes:

- **argo_floats**: ARGO float metadata
- **profiles**: ARGO profile data
- **measurements**: Temperature, salinity, pressure measurements
- **bgc_data**: Biogeochemical data (oxygen, chlorophyll, etc.)
- **user_contexts**: User context and preferences

## API Endpoints

### Query Endpoint
- **POST** `/api/v1/query`: Process natural language query

### Profile Endpoints
- **GET** `/api/v1/profiles`: Get profiles with filtering
- **GET** `/api/v1/profiles/{profile_id}`: Get a single profile

### Float Endpoints
- **GET** `/api/v1/floats`: Get floats with filtering
- **GET** `/api/v1/floats/{float_id}`: Get a single float

### Health Endpoints
- **GET** `/health`: Health check
- **GET** `/ready`: Readiness check

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running and accessible
- Check that PostGIS and TimescaleDB extensions are installed
- Verify database credentials in .env

### Redis Connection Issues
- Ensure Redis is running and accessible
- Check Redis URL in .env

### Qdrant Connection Issues
- Ensure Qdrant is running and accessible
- Check Qdrant URL in .env

### Frontend Not Connecting to Backend
- Check that backend is running on port 8000
- Verify VITE_API_URL in frontend .env
- Check CORS settings in backend

## Next Steps

1. **Configure LLM model**: Set `HUGGINGFACE_MODEL` (default works out of the box)
2. **Set up Mapbox**: Add your Mapbox access token
3. **Load Real Data**: Replace sample data with real ARGO data
4. **Configure MCP Servers**: Set up MCP server integrations
5. **Add Redis Caching**: Implement Redis caching for queries
6. **Set up Monitoring**: Add Prometheus metrics and logging

## Production Deployment

For production deployment:

1. **Set environment variables** for production
2. **Use production database** (managed PostgreSQL with PostGIS and TimescaleDB)
3. **Set up Redis cluster** for caching
4. **Configure Qdrant** for vector storage
5. **Set up monitoring** (Prometheus, Grafana)
6. **Configure logging** (structured logging with ELK stack)
7. **Set up CI/CD** pipeline
8. **Configure SSL/TLS** certificates
9. **Set up authentication** (JWT tokens)
10. **Configure rate limiting** and security headers

## Support

For issues and questions, please open an issue on GitHub.

