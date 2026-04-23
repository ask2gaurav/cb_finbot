# Role-Gated RAG Platform

A multi-tier RAG platform leveraging Python 3.13, FastAPI, Docling, Qdrant, Semantic Router, and React Router 7.

## Local Development

1. Setup environment variables:
   `cp .env.example .env` (Add your GROQ_API_KEY)
   
2. Start all services (Backend, Frontend, MongoDB, Qdrant):
   `docker compose up -d --build`

   *The backend will automatically start using Python 3.13 and has hot-reloading enabled. The frontend will be served via React Router.*

3. Access the application:
   - Unified App (via NGINX): `http://localhost`
   - Backend API directly: `http://localhost:8000/api/v1`
   - MongoDB GUI (Mongo Express): `http://localhost:8081`

## Production Deployment

1. Set `APP_ENV=production` and generate a strong `SECRET_KEY` and `JWT_SECRET`.
2. Configure `ALLOWED_ORIGINS` to your production frontend URL.
3. Build and run via Docker Compose:
   `docker compose -f docker-compose.yml up -d --build`
4. Apply reverse proxy (NGINX + Certbot for SSL).

## Security Hardening
- Rotate `SECRET_KEY` and `JWT_SECRET`
- Use strongly hashed passwords
- Set `ALLOWED_ORIGINS` properly
- Least privilege access for MongoDB user
- Enable Qdrant API key (`service.api_key` in `config.yaml`)

## Evaluation
To run RAGAs evaluation against the sample dataset:
`python backend/evaluation/run_ragas.py --dataset backend/evaluation/ground_truth_40qa.json`
