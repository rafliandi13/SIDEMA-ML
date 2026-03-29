# SIDEMA-ML FastAPI Backend (MVP)

Production-minded MVP backend for mobile anemia screening with separate pipelines for:
- nail image analysis
- conjunctiva image analysis

## Tech Stack
- FastAPI (Python 3.11)
- MinIO (S3-compatible object storage)
- Supabase (PostgreSQL via Supabase API)
- Docker / Docker Compose

## Project Structure

```text
app/
  api/
    routes/                # health, models, predict, history endpoints
    deps.py                # dependency wiring
    responses.py           # success envelope helper
  core/
    config.py              # env-driven settings
    exceptions.py          # custom app exceptions
    handlers.py            # centralized error handlers
    logging.py             # logging setup
  schemas/                 # typed request/response/domain models
  services/
    inference/             # NailInferenceService, ConjunctivaInferenceService
    storage/               # MinioStorageService
    database/              # SupabaseService
    image/                 # upload + quality validation
  repositories/
    predictions.py         # persistence access for predictions table
  utils/
    file_utils.py
    datetime_utils.py
migrations/
  001_create_predictions.sql
tests/
models/
  nail/                    # place mlp_model.joblib + feature_scaler.joblib
  conjunctiva/             # place Model_MobileNet.h5
Dockerfile
docker-compose.yml
.env.example
requirements.txt
```

## Required Endpoints
- `GET /health`
- `GET /models/info`
- `POST /predict/nail`
- `POST /predict/conjunctiva`
- `GET /history/{user_id}`
- `GET /history/{user_id}/{prediction_id}`

## Response Envelope

Success:
```json
{
  "success": true,
  "data": {},
  "message": "..."
}
```

Error:
```json
{
  "success": false,
  "error": {
    "code": "...",
    "message": "..."
  }
}
```

## Environment Setup
1. Copy env template:
```bash
cp .env.example .env
```
2. Isi konfigurasi infrastruktur yang sudah Anda siapkan:
   - `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET_NAME`
   - `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (atau `SUPABASE_KEY`)
3. Ensure model artifact paths exist if you want real inference:
   - Nail: `NAIL_MLP_MODEL_PATH`, `NAIL_SCALER_MODEL_PATH`
   - Conjunctiva: `CONJUNCTIVA_MODEL_PATH`

## Database Setup (Supabase)
Run SQL in Supabase SQL editor:
- `migrations/001_create_predictions.sql`

## Run Locally (without Docker)
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run with Docker Compose
```bash
cp .env.example .env
docker compose up --build
```
- API: `http://localhost:8000`

Catatan: `docker-compose.yml` sekarang hanya menjalankan service API. MinIO dan Supabase diasumsikan sudah tersedia di environment Anda.

## Prediction Flow
Each predict endpoint does:
1. Parse multipart form-data (`user_id`, `image`, optional `threshold`)
2. Validate MIME, extension, file size
3. Validate readability + minimum dimensions
4. Run blur/brightness placeholder quality checks
5. Upload original file to MinIO key format:
   - `raw/{user_id}/{method}/{yyyy}/{mm}/{uuid}.{ext}`
6. Run method-specific inference service
7. Save prediction metadata/history to Supabase
8. Return standardized response for mobile clients

## Real Model Integration: Files to Edit
- Nail pipeline:
  - `app/services/inference/nail.py`
- Conjunctiva pipeline:
  - `app/services/inference/conjunctiva.py`
- Model config paths/thresholds:
  - `app/core/config.py`
  - `.env`

## Notes on Model Strategy
- Hybrid mode implemented:
  - If model artifacts are present and loadable, service uses real inference path.
  - If not, service falls back to deterministic placeholder output while preserving API shape.

## Testing
```bash
pytest -q
```

## Priority Next Steps
1. Add authentication and authorization layer (JWT or Supabase Auth).
2. Add async processing queue for inference-heavy workloads.
3. Add richer observability (request IDs, tracing, metrics).
4. Add stricter validation and calibration using real model evaluation data.
5. Add CI/CD pipeline with automated tests and security scans.
