# Solar Product Intelligence Backend System

A production-ready FastAPI backend for managing solar products with **strict data integrity rules**.

## Features

- **Strict Data Validation**: Every product requires an official datasheet
- **Admin-Controlled Ingestion**: Only admins can add products and data
- **PDF Text Extraction**: Extract text from datasheets for AI usage
- **Automated Spec Extraction**: Parse technical specifications from documents
- **Product Validation Engine**: Enforce quality standards automatically
- **JWT Authentication**: Secure admin access with JWT tokens

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Production database
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **PyMuPDF** - PDF text extraction
- **JWT** - Authentication tokens

## Deployment

### 🚂 Railway (Recommended)

1. **Connect GitHub Repository**
   - Go to [Railway](https://railway.app)
   - Connect your GitHub account
   - Select this repository

2. **Add PostgreSQL Database**
   - In Railway dashboard, click "Add Plugin"
   - Select "PostgreSQL"
   - Railway will automatically set `DATABASE_URL`

3. **Configure Environment Variables**
   - In Railway project settings, add:
     ```
     SECRET_KEY=<generate-a-random-secret-key>
     APP_NAME=Solar Product Intelligence
     DEBUG=false
     ```

4. **Deploy**
   - Railway will automatically detect and deploy
   - Or manually trigger a deployment

5. **Seed Database**
   - Use Railway's terminal or connect via CLI:
   ```bash
   railway run python -m app.db.seed
   ```

### Docker

```bash
# Build image
docker build -t solar-product-api .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  -e SECRET_KEY=your-secret-key \
  solar-product-api
```

### Manual Deployment

```bash
pip install -r requirements.txt
python -m app.db.seed
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Project Structure

```
/workspace/project/simulator/
├── app/
│   ├── api/           # API routes
│   │   ├── admin/     # Admin-only endpoints
│   │   ├── public/    # Public endpoints
│   │   └── auth.py    # Authentication routes
│   ├── core/          # Core utilities
│   │   ├── config.py  # Configuration management
│   │   ├── database.py # Database connection
│   │   └── security.py # JWT authentication
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   │   ├── pdf_extractor.py
│   │   ├── spec_extractor.py
│   │   └── validation_engine.py
│   └── db/           # Database utilities
├── alembic/          # Database migrations
├── tests/            # Test suite
├── uploads/          # File uploads
├── main.py           # Application entry point
├── Dockerfile        # Docker configuration
├── railway.json      # Railway configuration
└── requirements.txt   # Dependencies
```

## Data Integrity Rules

1. **No external datasets** - All data is admin-controlled
2. **No public/user uploads** - Only admin ingestion
3. **Every product MUST have an official datasheet** - This is a strict requirement
4. **No datasheet = reject product** - Products without datasheets are rejected
5. **All specs must be extracted from datasheet text** - Manual spec entry is not allowed
6. **System stores both structured specs and raw document text** - For future AI usage

## Database Schema

### Tables

1. **users** - Admin user accounts
2. **companies** - Solar product manufacturers
3. **categories** - Product categories (battery, inverter, solar_panel, charge_controller)
4. **products** - Solar products with datasheet requirements
5. **documents** - Product datasheets and manuals with extracted text
6. **product_specifications** - Flexible key-value specifications
7. **company_metrics** - Company performance tracking
8. **reviews** - Product and company reviews

## Required Specifications by Category

### Battery
- voltage
- capacity
- cycle_life

### Inverter
- rated_power
- battery_voltage_range
- max_charge_current

### Solar Panel
- wattage
- Voc
- Isc

### Charge Controller
- max_input_voltage
- rated_current
- efficiency

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new admin user
- `POST /api/auth/login` - Login and get JWT token

### Admin Endpoints (Require JWT)
- `GET/POST /api/admin/companies` - Manage companies
- `GET/POST /api/admin/products` - Manage products
- `GET/POST /api/admin/categories` - Manage categories
- `POST /api/admin/products/{id}/documents` - Upload documents
- `POST /api/admin/products/{id}/validate` - Validate product
- `GET/POST /api/admin/reviews` - Manage reviews

### Public Endpoints
- `GET /api/companies` - List verified companies
- `GET /api/products` - List approved products
- `GET /api/categories` - List categories
- `GET /api/products/{id}/specs` - Get product specifications

## Authentication

Admin endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

Default admin credentials (change in production!):
- Username: `admin`
- Password: `admin123`

## Workflow

### Adding a New Product

1. **Create Company** (if not exists)
   ```bash
   POST /api/admin/companies
   ```

2. **Create Product** (with datasheet URL required)
   ```bash
   POST /api/admin/products
   {
     "company_id": 1,
     "category_id": 1,
     "model_name": "ABC-123",
     "product_name": "Solar Battery 100Ah",
     "datasheet_file_url": "https://example.com/datasheet.pdf"
   }
   ```

3. **Upload Document**
   ```bash
   POST /api/admin/products/{id}/documents
   ```

4. **Extract Text**
   ```bash
   POST /api/admin/products/{id}/documents/{doc_id}/extract
   ```

5. **Extract Specifications**
   ```bash
   POST /api/admin/products/{id}/documents/{doc_id}/extract-specs
   ```

6. **Validate Product**
   ```bash
   POST /api/admin/products/{id}/validate
   ```

7. **Approve/Reject**
   ```bash
   POST /api/admin/products/{id}/approve
   # or
   POST /api/admin/products/{id}/reject
   ```

## Testing

```bash
pytest tests/ -v
```

## License

MIT License
