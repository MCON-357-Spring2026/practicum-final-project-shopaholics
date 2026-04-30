# FitVision — AI Virtual Try-On App

A full-stack web app where users upload a photo of themselves, pick a clothing item from a live catalog, and see an AI-generated image of themselves wearing it.

**Jira:** https://mcon152.atlassian.net/browse/M3S-17
**Docs:** https://mcon152.atlassian.net/wiki/spaces/team9d39f66a69dc4fdaa5b025a0c78b48b6/overview

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, React Router, Axios |
| Backend | Flask, SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt, Flask-Migrate |
| Database | PostgreSQL (Render managed or AWS RDS) |
| File Storage | AWS S3 (user photos + AI results) |
| Product Catalog | RapidAPI (ASOS or Kohl's) |
| AI Try-On Engine | Fashn.ai API |
| Deployment | Render (backend + frontend + DB via render.yaml) |

---

## Project Structure

```
practicum-final-project-shopaholics/
├── render.yaml                        ← Render deployment config (all 3 services)
├── README.md
│
├── backend/
│   ├── wsgi.py                        ← Entry point (reads PORT from env)
│   ├── config.py                      ← Dev / Prod / Testing configs
│   ├── requirements.txt
│   ├── .env.example                   ← Copy to .env and fill in keys
│   └── app/
│       ├── __init__.py                ← create_app() factory
│       ├── extensions.py              ← db, migrate, jwt, bcrypt, cors, limiter
│       ├── models/
│       │   ├── __init__.py            ← imports all models (required for Alembic)
│       │   ├── user.py                ← User (id, email, password_hash, created_at)
│       │   ├── product.py             ← Product (cached from RapidAPI)
│       │   └── tryon_job.py           ← TryOnJob (PENDING→PROCESSING→DONE|FAILED)
│       ├── routes/
│       │   ├── auth.py                ← POST /register, POST /login, GET /me, POST /logout
│       │   ├── products.py            ← GET /search, GET /<id> (DB cache + RapidAPI)
│       │   ├── uploads.py             ← POST /person, DELETE /<key>
│       │   └── tryon.py               ← POST /generate, GET /jobs/<id>, GET /history
│       ├── services/
│       │   ├── s3.py                  ← upload_file, delete_file, get_presigned_url
│       │   ├── rapidapi.py            ← search_products, get_product
│       │   └── fashn.py               ← submit_tryon, poll_result
│       └── tasks/
│           └── tryon_worker.py        ← background thread: Fashn.ai → S3 → DB update
│
└── frontend/
    ├── index.html
    ├── vite.config.js                 ← dev proxy /api → localhost:5000
    ├── package.json
    └── src/
        ├── main.jsx                   ← BrowserRouter + AuthProvider
        ├── App.jsx                    ← route definitions
        ├── api/
        │   ├── client.js              ← axios + JWT interceptor + 401 redirect
        │   ├── auth.js
        │   ├── products.js
        │   ├── uploads.js
        │   └── tryon.js
        ├── context/
        │   └── AuthContext.jsx        ← user state, login/logout, token restore
        ├── components/
        │   ├── ProtectedRoute.jsx
        │   ├── ImageUpload.jsx        ← drag+drop, file validation, S3 upload
        │   ├── ProductCard.jsx        ← product tile with "Try On" button
        │   └── TryOnStatus.jsx        ← polls every 3s, shows result image
        └── pages/
            ├── Login.jsx              ← login + register in one form
            ├── Catalog.jsx            ← search bar + product grid
            └── FittingRoom.jsx        ← photo upload + garment + try-on trigger
```

---

## API Routes

### Auth — `/api/auth`
| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/register` | No | Create account |
| POST | `/login` | No | Returns JWT access token |
| GET | `/me` | Yes | Current user profile |
| POST | `/logout` | No | Client deletes token |

### Products — `/api/products`
| Method | Route | Auth | Description |
|---|---|---|---|
| GET | `/search?q=&category=&limit=` | Yes | Search RapidAPI, cache in DB |
| GET | `/<id>` | Yes | Single product (refreshes stale cache) |

### Uploads — `/api/uploads`
| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/person` | Yes | Upload user photo → S3 |
| DELETE | `/<key>` | Yes | Delete own uploaded image |

### Try-On — `/api/tryon`
| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/generate` | Yes | Create job, kick off async worker |
| GET | `/jobs/<job_id>` | Yes | Poll status + presigned result URL |
| GET | `/history` | Yes | Paginated past try-ons |
| DELETE | `/jobs/<job_id>` | Yes | Delete job + S3 result |

### Health
| Method | Route | Description |
|---|---|---|
| GET | `/health` | Liveness check for Render |

---

## Database Schema

```sql
users
  id            VARCHAR(36) PRIMARY KEY
  email         VARCHAR(255) UNIQUE NOT NULL
  password_hash VARCHAR(255) NOT NULL
  created_at    TIMESTAMPTZ NOT NULL

products
  id            VARCHAR(36) PRIMARY KEY
  external_id   VARCHAR(255) UNIQUE NOT NULL   -- RapidAPI product ID
  title         VARCHAR(500)
  brand         VARCHAR(255)
  image_url     TEXT
  category      VARCHAR(100)
  price         NUMERIC(10,2)
  raw_data      JSON                           -- full API response
  cached_at     TIMESTAMPTZ NOT NULL

tryon_jobs
  id                  VARCHAR(36) PRIMARY KEY
  user_id             VARCHAR(36) FK → users.id  (CASCADE DELETE)
  product_id          VARCHAR(36) FK → products.id (SET NULL)
  person_image_url    TEXT NOT NULL
  garment_image_url   TEXT NOT NULL
  fashn_prediction_id VARCHAR(255)
  status              ENUM(PENDING, PROCESSING, DONE, FAILED)
  result_url          TEXT
  error_message       TEXT
  created_at          TIMESTAMPTZ NOT NULL
  completed_at        TIMESTAMPTZ
```

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```bash
FLASK_APP=wsgi.py
FLASK_ENV=development
SECRET_KEY=                    # any random string
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fitvision_dev
JWT_SECRET_KEY=                # any random string
FRONTEND_URL=http://localhost:5173

# AWS S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET=

# RapidAPI
RAPIDAPI_KEY=
RAPIDAPI_HOST=                 # e.g. asos-api.p.rapidapi.com

# Fashn.ai
FASHN_API_KEY=
FASHN_API_BASE_URL=https://api.fashn.ai/v1
```

---

## Local Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # fill in values

flask db init               # first time only
flask db migrate -m "initial schema"
flask db upgrade

flask run                   # http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173 (proxies /api → :5000)
```

---

## Deployment (Render)

`render.yaml` at repo root defines all three services.

1. Push repo to GitHub
2. Render → New → Blueprint → connect repo
3. Set `sync: false` env vars manually in Render dashboard:

**On `fitvision-backend`:**
- `FRONTEND_URL` → `https://fitvision-frontend.onrender.com`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`
- `RAPIDAPI_KEY`, `FASHN_API_KEY`

**On `fitvision-frontend`:**
- `VITE_API_URL` → `https://fitvision-backend.onrender.com/api`

4. Redeploy both services
5. Verify: `curl https://fitvision-backend.onrender.com/health`

### Common Errors
| Error | Fix |
|---|---|
| `KeyError: 'SECRET_KEY'` | Add env var in Render dashboard |
| CORS blocked in browser | `FRONTEND_URL` must match frontend URL exactly, no trailing slash |
| S3 upload `403` | Check IAM policy has `s3:PutObject` on your bucket |
| Frontend API calls fail | `VITE_API_URL` not set or missing `/api` suffix |
| Try-on stuck on PROCESSING | Dyno restarted mid-job — resubmit the job |

---

## What's Done

- [x] Flask app factory with all extensions wired
- [x] Environment-based config (dev / prod / test)
- [x] SQLAlchemy models: `User`, `Product`, `TryOnJob`
- [x] Flask-Migrate setup
- [x] Auth routes: register, login, JWT, protected `/me`
- [x] S3 service: upload, delete, presigned URL, download
- [x] Upload route with file validation (type + 10MB limit)
- [x] RapidAPI product service with DB caching + TTL
- [x] Fashn.ai service: submit + polling with timeout
- [x] Async try-on worker (background thread)
- [x] Try-on routes: generate, poll, history, delete
- [x] React app: Vite + React Router + AuthContext
- [x] Axios client with JWT interceptor + 401 redirect
- [x] All API wrappers: auth, products, uploads, tryon
- [x] Pages: Login, Catalog, FittingRoom
- [x] Components: ImageUpload (drag+drop), ProductCard, TryOnStatus (polling)
- [x] ProtectedRoute
- [x] `render.yaml` for full Render deployment
- [x] Deployment guide with step-by-step checklist + common errors

---

## What's Left

- [ ] **Pick catalog API** — ASOS or Kohl's, then update `_upsert_product()` in `backend/app/routes/products.py` to match that API's response field names
- [ ] **Get API keys** — RapidAPI (ASOS/Kohl's), Fashn.ai, AWS IAM
- [ ] **Run migrations locally** — `flask db init && flask db migrate && flask db upgrade`
- [ ] **End-to-end test** — register → search → upload photo → try on → view result
- [ ] **Friendly error for Fashn.ai rejection** — when AI can't detect a human in the photo, show a clear message instead of generic "FAILED"
- [ ] **Saved outfits / favorites** (check rubric) — history endpoint exists; add explicit save button if rubric requires it
- [ ] **Architecture diagram** — export a clean diagram image for final deliverable
- [ ] **Elevator pitch** — 30-second pitch for demo day
- [ ] **Final rubric check** — verify every grading criterion before submission

---

## Try-On Flow (end to end)

```
1. User uploads photo       POST /api/uploads/person → stored in S3
2. User selects product     navigates to /fitting-room with product data
3. User clicks "Try It On"  POST /api/tryon/generate → returns job_id immediately
4. Background thread fires  calls Fashn.ai with both image URLs
5. Worker polls Fashn.ai    every 5s until DONE or FAILED (max 3 min)
6. Result downloaded        saved to S3 as results/{user_id}/{uuid}.jpg
7. Job updated in DB        status=DONE, result_url=S3 key
8. Frontend polls            GET /api/tryon/jobs/{job_id} every 3s
9. Result displayed         presigned S3 URL rendered in TryOnStatus
```
