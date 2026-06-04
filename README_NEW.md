# FitVision - AI Virtual Try-On Shopping Platform

FitVision is a modern e-commerce platform that allows users to virtually try on clothes using AI-powered technology. Users can upload their photos and see how different garments would look on them before making a purchase.

## 🚀 Live Demo

- **Frontend**: [https://fitvision-frontend.onrender.com](https://fitvision-frontend.onrender.com)
- **Backend API**: [https://fitvision-backend.onrender.com](https://fitvision-backend.onrender.com)

## ✨ Features

- **Virtual Try-On**: Upload your photo and try on clothes virtually using AI models
- **Smart Model Selection**: Automatically uses OOTDiffusion for dresses (full-body) and IDM-VTON for tops
- **Product Catalog**: Browse and search through a curated collection of wearable items
- **User Authentication**: Secure registration and login with JWT tokens
- **Try-On History**: View and manage your previous virtual try-on sessions
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (Flask-JWT-Extended)
- **Image Storage**: Cloudinary
- **AI Models**: HuggingFace (IDM-VTON, OOTDiffusion)
- **Background Tasks**: Thread-based workers
- **Testing**: Pytest with comprehensive coverage
- **Architecture**: Repository pattern for data access

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **API Client**: Axios with JWT interceptor
- **Routing**: React Router v6

### Infrastructure
- **Hosting**: Render.com
- **Database**: PostgreSQL (Render managed)
- **CI/CD**: Automated deployment via render.yaml

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Cloudinary account
- HuggingFace API token

## 🔧 Installation

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/practicum-final-project-shopaholics.git
cd practicum-final-project-shopaholics/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt  # For running tests
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

6. Start the backend server:
```bash
python wsgi.py
# or
flask run
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd ../frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🧪 Testing

### Running Backend Tests

```bash
cd backend

# Run all tests with coverage
./run_tests.sh

# Run only unit tests
./run_tests.sh unit

# Run only integration tests
./run_tests.sh integration

# Run tests with pytest directly
pytest tests/ -v
```

### Test Coverage

The project includes comprehensive test coverage for:
- **Models**: User, Product, TryOnJob
- **Repositories**: Data access layer testing
- **Services**: Business logic testing
- **Routes**: API endpoint testing

## 📁 Project Structure

```
practicum-final-project-shopaholics/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── repositories/    # Data access layer (Repository pattern)
│   │   ├── routes/          # API endpoints (Controllers)
│   │   ├── services/        # Business logic layer
│   │   ├── tasks/           # Background job processing
│   │   └── extensions.py    # Flask extensions initialization
│   ├── migrations/          # Alembic database migrations
│   ├── tests/              # Comprehensive test suite
│   │   ├── models/         # Model tests
│   │   ├── repositories/   # Repository tests
│   │   ├── services/       # Service tests
│   │   └── routes/         # API route tests
│   ├── config.py           # Application configuration
│   ├── requirements.txt    # Production dependencies
│   ├── requirements-test.txt # Testing dependencies
│   └── wsgi.py            # Application entry point
│
├── frontend/
│   ├── src/
│   │   ├── api/            # API client modules
│   │   ├── components/     # Reusable React components
│   │   ├── context/        # React Context for state management
│   │   ├── pages/          # Page components
│   │   └── App.jsx         # Main application component
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite configuration
│
└── render.yaml             # Render deployment configuration
```

## 🔌 API Documentation

### Authentication Endpoints

- `POST /api/auth/register` - Register new user
  ```json
  {
    "email": "user@example.com",
    "password": "secure_password"
  }
  ```

- `POST /api/auth/login` - Login user
  ```json
  {
    "email": "user@example.com",
    "password": "secure_password"
  }
  ```

- `GET /api/auth/me` - Get current user (requires authentication)

### Product Endpoints

- `GET /api/products/featured` - Get featured products
- `GET /api/products/search?q={query}&category={category}&limit={limit}` - Search products
- `GET /api/products/{id}` - Get single product details

### Virtual Try-On Endpoints

- `POST /api/tryon/generate` - Create new try-on job
  ```json
  {
    "person_image_url": "https://...",
    "garment_image_url": "https://...",
    "product_id": "product_uuid"
  }
  ```

- `GET /api/tryon/jobs/{id}` - Get job status and result
- `GET /api/tryon/history?page={page}&per_page={per_page}` - Get user's try-on history
- `DELETE /api/tryon/jobs/{id}` - Delete try-on job and results

### Upload Endpoints

- `POST /api/uploads/image` - Upload user image
  - Accepts: JPG, JPEG, PNG, GIF, WEBP
  - Max size: 10MB

## 🚀 Deployment

The application is configured for deployment on Render.com using the `render.yaml` file.

### Deploy to Render

1. Push your code to GitHub
2. Create a new account on [Render.com](https://render.com)
3. Create a new Blueprint instance
4. Connect your GitHub repository
5. Render will automatically create:
   - Backend web service
   - Frontend static site
   - PostgreSQL database

### Environment Variables

Configure these in your Render dashboard:

**Backend Service**:
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key
- `DATABASE_URL` - Provided by Render
- `CLOUDINARY_URL` - Your Cloudinary URL
- `HUGGINGFACE_API_TOKEN` - Your HuggingFace API token
- `FRONTEND_URL` - Your frontend URL (for CORS)

**Frontend Service**:
- `VITE_API_URL` - Your backend API URL

## 🏗️ Architecture

### Backend Architecture

The backend follows a layered architecture pattern:

1. **Routes (Controllers)** - Handle HTTP requests and responses
2. **Services** - Contains business logic
3. **Repositories** - Data access layer with database operations
4. **Models** - SQLAlchemy ORM models

### Key Design Patterns

- **Repository Pattern**: Abstracts data access logic
- **Service Layer**: Separates business logic from controllers
- **Factory Pattern**: Flask app factory for better testing
- **Background Workers**: Asynchronous job processing for AI operations

### Database Schema

- **Users**: Authentication and user profiles
- **Products**: Cached product data from external API
- **TryOnJobs**: Virtual try-on job tracking with status management

## 🔒 Security Features

- Password hashing with bcrypt
- JWT-based authentication
- Request rate limiting
- File type validation for uploads
- CORS configuration
- SQL injection protection via ORM

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- HuggingFace for AI models (IDM-VTON, OOTDiffusion)
- DummyJSON for product catalog API
- Cloudinary for image storage and management
- Render.com for hosting infrastructure