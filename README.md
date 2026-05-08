# RIDE_BOOKING_SYSTEM-AI_SDA_DBS-

FastAPI backend for a complete ride booking system with authentication, ride management, and payment processing.

## Features

- 🔐 **Authentication**: User registration, login, JWT-based session management
- 🚗 **Ride Management**: Create, accept, start, complete, and cancel rides
- 💳 **Payment Processing**: Secure payment creation, confirmation, refunds, and history
- 📊 **Ride History**: Comprehensive ride and payment history with pagination
- ⭐ **Driver Ratings**: Rate drivers after ride completion
- 🔒 **Security**: Password hashing, JWT tokens, secure payment handling

## Structure

The project follows a modular architecture with feature-based organization:

### Core Modules
- `app/` - Application bootstrap and configuration
- `core/` - Security, enums, and shared utilities
- `db/` - Database connection and SQL queries
- `exception/` - Custom exception handling
- `models/` - Data models and dataclasses
- `utils/` - Helper utilities (password hashing)

### Feature Modules
- `api/` - FastAPI routes and endpoints
- `repositories/` - Database access layer
- `schemas/` - Pydantic request/response models
- `services/` - Business logic layer
- `tests/` - Unit tests

## Setup

### Prerequisites
- Python 3.14+
- PostgreSQL database
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RIDE_BOOKING_SYSTEM-AI_SDA_DBS-
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/ride_booking
   SECRET_KEY=your-32-character-secret-key-here
   JWT_SECRET_KEY=your-32-character-jwt-secret-here
   ```

5. **Database setup**
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

## API Endpoints

### Authentication Routes
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT tokens)
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout (revoke refresh token)
- `GET /api/auth/me` - Get current user information

### Ride Management Routes
- `POST /api/rides/create` - Create a new ride request
- `GET /api/rides/{ride_id}` - Get ride details
- `GET /api/rides/history` - Get user's ride history (paginated)
- `PATCH /api/rides/{ride_id}/accept` - Accept a ride (driver only)
- `PATCH /api/rides/{ride_id}/start` - Start a ride (driver only)
- `PATCH /api/rides/{ride_id}/complete` - Complete a ride (driver only)
- `POST /api/rides/{ride_id}/cancel` - Cancel a ride
- `POST /api/rides/{ride_id}/rating` - Rate a driver after ride completion

### Payment Routes
- `POST /api/payments/create` - Create a payment for a ride
- `GET /api/payments/{payment_id}` - Get payment status
- `POST /api/payments/{payment_id}/confirm` - Confirm payment completion
- `POST /api/payments/{payment_id}/refund` - Process payment refund
- `GET /api/payments/history` - Get payment history (paginated)
- `POST /api/payments/methods` - Get available payment methods
- `POST /api/payments/webhook/payment-gateway` - Payment gateway webhook

## Testing

Run the complete test suite:

```bash
pytest tests/unit/ -v
```

The test suite covers:
- Authentication services (registration, login, session management)
- Ride lifecycle management (creation, acceptance, completion)
- Payment processing (creation, confirmation, refunds)
- API endpoint validation

## Database Schema

The application uses PostgreSQL with the following main tables:

- `users` - User accounts and authentication data
- `rides` - Ride requests and lifecycle information
- `ride_history` - Historical ride records
- `payments` - Payment transactions and status

Run migrations with:
```bash
alembic upgrade head
```

## Development

### Code Quality
- Follows consistent patterns across auth, rides, and payments modules
- Comprehensive error handling with custom exceptions
- Type hints and Pydantic validation throughout
- Async/await patterns for database operations

### Architecture Principles
- **Separation of Concerns**: Clear separation between API, business logic, and data access
- **Dependency Injection**: Services and repositories injected via FastAPI dependencies
- **Domain-Driven Design**: Feature-based module organization
- **Test-Driven Development**: Comprehensive unit test coverage

## Deployment

### Production Checklist
- [ ] Set secure `SECRET_KEY` and `JWT_SECRET_KEY` (32+ characters)
- [ ] Configure production PostgreSQL database
- [ ] Enable HTTPS/SSL
- [ ] Set up payment gateway integration
- [ ] Configure logging and monitoring
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Set appropriate environment variables

### Docker Deployment (Optional)
```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Follow the existing code patterns and architecture
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure all tests pass before submitting PRs

## License

This project is licensed under the MIT License.
