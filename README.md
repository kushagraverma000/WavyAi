# WavyAI: AI-Powered ARGO Ocean Data Platform

WavyAI is a production-ready AI-powered conversational system for oceanographic ARGO float data. It enables researchers, students, coastal managers, NGOs, fisheries, and shipping planners to query, explore, and visualize oceanographic data using natural language.

## Features

- 🌊 **Natural Language Querying**: Ask questions about ocean data in plain English
- 🎯 **Adaptive Responses**: Intelligently adapts to user expertise level and needs
- 📊 **Interactive Visualizations**: Dynamic maps, charts, and plots based on user type
- 🔍 **Hybrid Search**: Combines vector similarity search with SQL filtering
- 👥 **Multi-Audience Support**: Tailored experiences for researchers, students, managers, and more
- 📈 **Real-time Data**: Access to latest ARGO float data with incremental updates
- 🚀 **Production Ready**: Scalable architecture with Docker, monitoring, and error handling

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI   │────▶│ PostgreSQL  │
│  Frontend   │     │   Backend   │     │  + PostGIS  │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ├────▶│   Qdrant   │ (Vector DB)
                            │     └────────────┘
                            ├────▶│   Redis    │ (Cache)
                            │     └────────────┘
                            └────▶│   Celery   │ (Background Jobs)
                                  └────────────┘
```

## Tech Stack

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL with PostGIS and TimescaleDB
- Qdrant (Vector Database)
- Redis (Caching)
- Celery (Async Tasks)
- LangChain (LLM Orchestration)

### Frontend
- React 18+ with TypeScript
- TailwindCSS
- Mapbox GL JS
- Plotly.js & Recharts
- Vite (Build Tool)

### AI/ML
- LangChain
- Hugging Face Transformers (local open-source models)
- Open-source sentence-transformers embeddings

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd WavyAI
```

2. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. Start services with Docker Compose:
```bash
docker-compose up -d
```

4. Initialize the database:
```bash
cd backend
python scripts/init_db.py
python scripts/load_sample_data.py
```

5. Start the backend (in development):
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. Start the frontend:
```bash
cd frontend
npm install
npm run dev
```

7. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
WavyAI/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration, security
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── scripts/            # Utility scripts
│   ├── tests/              # Tests
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── hooks/          # Custom hooks
│   │   └── App.tsx
│   └── package.json
├── data/                   # Data files
│   ├── raw/               # Raw NetCDF files
│   └── processed/         # Processed data
├── docker-compose.yml      # Docker configuration
└── README.md
```

Place historical ARGO NetCDF files under `data/raw/<year>/<month>/<day>/`. For example:

```
data/raw/2015/07/03/argo_profiles_20150703.nc
```

The ingestion service traverses this hierarchy recursively when loading data.

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Environment Variables

See `.env.example` for all required environment variables. Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: Optional, only needed if you switch embeddings to OpenAI
- `HUGGINGFACE_MODEL`: Hugging Face model for text generation (default: `HuggingFaceH4/zephyr-7b-alpha`)
- `HUGGINGFACE_MAX_NEW_TOKENS`: Maximum tokens for generated responses
- `MAPBOX_ACCESS_TOKEN`: Mapbox token for maps

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues and questions, please open an issue on GitHub.

