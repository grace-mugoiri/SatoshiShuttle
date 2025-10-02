#!/usr/bin/env python3
"""
RideShare Connect - Setup Script
Automated setup for the P2P carpooling platform with Bitcoin payments
"""

import os
import sys
import subprocess
import json
import secrets
from pathlib import Path

class RideShareSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.frontend_dir = self.project_root / "frontend"
        
    def print_step(self, step, message):
        print(f"\n{'='*50}")
        print(f"Step {step}: {message}")
        print(f"{'='*50}")
        
    def run_command(self, command, cwd=None):
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                cwd=cwd,
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {command}")
            print(f"Error: {e.stderr}")
            return None
            
    def create_directory_structure(self):
        """Create project directory structure"""
        self.print_step(1, "Creating Directory Structure")
        
        directories = [
            "utils",
            "routes",
            "models",
            "tests",
            "static",
            "templates",
            ".github/workflows",
            "frontend/src/components",
            "frontend/src/utils",
            "frontend/src/services",
            "frontend/public"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {directory}")
            
    def generate_env_file(self):
        """Generate .env file with secure keys"""
        self.print_step(2, "Generating Environment Configuration")
        
        # Generate secure keys
        secret_key = secrets.token_hex(32)
        jwt_key = secrets.token_hex(32)
        
        env_content = f"""# RideShare Connect Environment Variables
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_key}
DATABASE_URL=sqlite:///rideshare.db

# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py

# Bitcoin Configuration
BITCOIN_RPC_HOST=localhost
BITCOIN_RPC_PORT=8332
BITCOIN_RPC_USER=your-rpc-user
BITCOIN_RPC_PASSWORD=your-rpc-password

# BTCPay Server (Optional)
BTCPAY_URL=https://your-btcpay-server.com
BTCPAY_API_KEY=your-btcpay-api-key

# Lightning Network (Optional)
LND_HOST=localhost:10009
LND_CERT_PATH=~/.lnd/tls.cert
LND_MACAROON_PATH=~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon

# Frontend/Backend URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:5000

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Production Database (PostgreSQL)
# DATABASE_URL=postgresql://username:password@localhost/rideshare_db
"""
        
        env_path = self.project_root / ".env"
        with open(env_path, "w") as f:
            f.write(env_content)
            
        print("✓ Generated .env file with secure keys")
        print("⚠️  Remember to update Bitcoin RPC credentials")
        
    def setup_python_backend(self):
        """Setup Python backend"""
        self.print_step(3, "Setting up Python Backend")
        
        # Check if virtual environment exists
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            print("Creating virtual environment...")
            self.run_command("python -m venv venv")
            
        # Activate virtual environment and install dependencies
        if sys.platform == "win32":
            pip_path = venv_path / "Scripts" / "pip"
            python_path = venv_path / "Scripts" / "python"
        else:
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"
            
        print("Installing Python dependencies...")
        dependencies = [
            "Flask==2.3.3",
            "Flask-SQLAlchemy==3.0.5",
            "Flask-JWT-Extended==4.5.3",
            "Flask-CORS==4.0.0",
            "python-dotenv==1.0.0",
            "requests==2.31.0",
            "Werkzeug==2.3.7",
            "pytest==7.4.3",
            "pytest-cov==4.1.0"
        ]
        
        for dep in dependencies:
            result = self.run_command(f'"{pip_path}" install {dep}')
            if result is not None:
                print(f"✓ Installed: {dep}")
            else:
                print(f"✗ Failed to install: {dep}")
                
    def setup_react_frontend(self):
        """Setup React frontend"""
        self.print_step(4, "Setting up React Frontend")
        
        if not self.frontend_dir.exists():
            print("Creating React app...")
            result = self.run_command("npx create-react-app frontend")
            if result is None:
                print("✗ Failed to create React app")
                return
                
        print("Installing additional React dependencies...")
        dependencies = [
            "react-router-dom",
            "lucide-react",
            "axios",
            "tailwindcss",
            "postcss",
            "autoprefixer"
        ]
        
        # Install dependencies
        for dep in dependencies:
            result = self.run_command(f"npm install {dep}", cwd=self.frontend_dir)
            if result is not None:
                print(f"✓ Installed: {dep}")
                
        # Initialize Tailwind CSS
        print("Initializing Tailwind CSS...")
        self.run_command("npx tailwindcss init -p", cwd=self.frontend_dir)
        
    def create_package_json_scripts(self):
        """Add custom scripts to package.json"""
        self.print_step(5, "Configuring Package.json Scripts")
        
        package_json_path = self.frontend_dir / "package.json"
        if package_json_path.exists():
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                
            # Add custom scripts
            package_data["scripts"].update({
                "start:dev": "REACT_APP_API_URL=http://localhost:5000 npm start",
                "build:prod": "REACT_APP_API_URL=https://your-api-domain.com npm run build",
                "test:coverage": "npm test -- --coverage --watchAll=false",
                "lint": "eslint src/",
                "format": "prettier --write src/"
            })
            
            # Add proxy for development
            package_data["proxy"] = "http://localhost:5000"
            
            with open(package_json_path, 'w') as f:
                json.dump(package_data, f, indent=2)
                
            print("✓ Updated package.json with custom scripts")
            
    def create_database_init_script(self):
        """Create database initialization script"""
        self.print_step(6, "Creating Database Initialization")
        
        init_db_content = """#!/usr/bin/env python3
\"\"\"
Database initialization script for RideShare Connect
\"\"\"

from app import app, db, User, Ride, Booking, Review
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    \"\"\"Initialize database with tables and sample data\"\"\"
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@rideshare.com',
                password_hash=generate_password_hash('admin123'),
                phone='+1234567890',
                bitcoin_address='bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'  # Example address
            )
            db.session.add(admin)
            
        # Create sample users
        sample_users = [
            {
                'username': 'alice_driver',
                'email': 'alice@example.com',
                'password': 'password123',
                'phone': '+1234567891',
                'bitcoin_address': 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'
            },
            {
                'username': 'bob_passenger',
                'email': 'bob@example.com',
                'password': 'password123',
                'phone': '+1234567892',
                'bitcoin_address': 'bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3'
            }
        ]
        
        for user_data in sample_users:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    phone=user_data['phone'],
                    bitcoin_address=user_data['bitcoin_address']
                )
                db.session.add(user)
                print(f"✓ Created user: {user_data['username']}")
        
        db.session.commit()
        print("✓ Database initialized successfully!")
        
        # Print summary
        user_count = User.query.count()
        ride_count = Ride.query.count()
        booking_count = Booking.query.count()
        
        print(f"\\nDatabase Summary:")
        print(f"Users: {user_count}")
        print(f"Rides: {ride_count}")
        print(f"Bookings: {booking_count}")

if __name__ == '__main__':
    init_database()
"""
        
        init_db_path = self.project_root / "init_db.py"
        with open(init_db_path, "w") as f:
            f.write(init_db_content)
            
        print("✓ Created database initialization script")
        
    def create_test_files(self):
        """Create basic test files"""
        self.print_step(7, "Creating Test Files")
        
        # Backend tests
        test_app_content = """import pytest
import json
from app import app, db, User, Ride, Booking

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_register_user(client):
    \"\"\"Test user registration\"\"\"
    response = client.post('/api/register', 
        json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'phone': '+1234567890'
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'User registered successfully' in data['message']

def test_login_user(client):
    \"\"\"Test user login\"\"\"
    # First register a user
    client.post('/api/register',
        json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }
    )
    
    # Then login
    response = client.post('/api/login',
        json={
            'username': 'testuser',
            'password': 'password123'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_get_rides(client):
    \"\"\"Test getting available rides\"\"\"
    response = client.get('/api/rides')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_bitcoin_price_endpoint(client):
    \"\"\"Test Bitcoin price endpoint\"\"\"
    response = client.get('/api/bitcoin/price')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'prices' in data
"""
        
        test_path = self.project_root / "tests" / "test_app.py"
        with open(test_path, "w") as f:
            f.write(test_app_content)
            
        # Frontend tests
        frontend_test_content = """import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

// Mock fetch
global.fetch = jest.fn();

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

beforeEach(() => {
  fetch.mockClear();
});

test('renders home page', () => {
  renderWithRouter(<App />);
  expect(screen.getByText(/Share Rides, Pay with Bitcoin/i)).toBeInTheDocument();
});

test('renders navigation', () => {
  renderWithRouter(<App />);
  expect(screen.getByText(/RideShare Connect/i)).toBeInTheDocument();
  expect(screen.getByText(/Find Rides/i)).toBeInTheDocument();
});

test('login form submission', async () => {
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({
      access_token: 'mock-token',
      user: { id: 1, username: 'testuser' }
    })
  });

  renderWithRouter(<App />);
  
  // Navigate to login
  fireEvent.click(screen.getByText(/Login/i));
  
  // Fill form
  fireEvent.change(screen.getByPlaceholderText(/Username/i), {
    target: { value: 'testuser' }
  });
  fireEvent.change(screen.getByPlaceholderText(/Password/i), {
    target: { value: 'password123' }
  });
  
  // Submit
  fireEvent.click(screen.getByText(/Sign in/i));
  
  await waitFor(() => {
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:5000/api/login',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'testuser', password: 'password123' })
      })
    );
  });
});
"""
        
        frontend_test_path = self.frontend_dir / "src" / "App.test.js"
        with open(frontend_test_path, "w") as f:
            f.write(frontend_test_content)
            
        print("✓ Created test files")
        
    def create_deployment_configs(self):
        """Create deployment configuration files"""
        self.print_step(8, "Creating Deployment Configurations")
        
        # Docker configuration
        dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run application
CMD ["python", "app.py"]
"""
        
        dockerfile_path = self.project_root / "Dockerfile"
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
            
        # Docker Compose
        docker_compose_content = """version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://rideshare:password@postgres:5432/rideshare_db
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: rideshare_db
      POSTGRES_USER: rideshare
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
"""
        
        compose_path = self.project_root / "docker-compose.yml"
        with open(compose_path, "w") as f:
            f.write(docker_compose_content)
            
        print("✓ Created Docker configuration files")
        
    def create_readme_and_docs(self):
        """Create comprehensive documentation"""
        self.print_step(9, "Creating Documentation")
        
        # API Documentation
        api_docs_content = """# RideShare Connect API Documentation

## Base URL
- Development: `http://localhost:5000/api`
- Production: `https://your-domain.com/api`

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /profile` - Get user profile (protected)

### Rides
- `GET /rides` - List available rides
- `POST /rides` - Create new ride (protected)
- `GET /my-rides` - Get user's offered rides (protected)

### Bookings
- `POST /bookings` - Book a ride (protected)
- `GET /my-bookings` - Get user's bookings (protected)

### Bitcoin Endpoints
- `GET /bitcoin/price` - Get current Bitcoin price
- `POST /bitcoin/convert` - Convert currency to Bitcoin
- `POST /bitcoin/validate-address` - Validate Bitcoin address
- `POST /bitcoin/create-payment` - Create Bitcoin payment (protected)
- `GET /bitcoin/fee-estimate` - Get network fee estimates

### Lightning Network
- `POST /bitcoin/lightning/create-invoice` - Create Lightning invoice (protected)
- `POST /bitcoin/lightning/pay-invoice` - Pay Lightning invoice (protected)

## Error Responses
All endpoints return errors in the following format:
```json
{
  "error": "Error message description"
}
```

## Rate Limiting
- 100 requests per minute per IP for public endpoints
- 1000 requests per minute for authenticated users

## Webhooks
- `POST /bitcoin/webhook/payment` - Bitcoin payment notifications
"""
        
        api_docs_path = self.project_root / "docs" / "API.md"
        os.makedirs(self.project_root / "docs", exist_ok=True)
        with open(api_docs_path, "w") as f:
            f.write(api_docs_content)
            
        print("✓ Created API documentation")
        
    def run_initial_tests(self):
        """Run initial tests to verify setup"""
        self.print_step(10, "Running Initial Tests")
        
        print("Testing Python backend...")
        if sys.platform == "win32":
            python_path = self.project_root / "venv" / "Scripts" / "python"
        else:
            python_path = self.project_root / "venv" / "bin" / "python"
            
        # Test imports
        test_result = self.run_command(f'"{python_path}" -c "from app import app; print(\'✓ Flask app imports successfully\')"')
        if test_result:
            print(test_result.strip())
            
        # Test React frontend
        if self.frontend_dir.exists():
            print("Testing React frontend...")
            test_result = self.run_command("npm test -- --passWithNoTests --watchAll=false", cwd=self.frontend_dir)
            if test_result:
                print("✓ React tests pass")
                
    def create_startup_scripts(self):
        """Create convenient startup scripts"""
        self.print_step(11, "Creating Startup Scripts")
        
        # Development startup script
        if sys.platform == "win32":
            start_dev_content = """@echo off
echo Starting RideShare Connect in Development Mode...

echo.
echo Starting Backend...
start "Backend" cmd /k "venv\\Scripts\\activate && python app.py"

timeout /t 3

echo.
echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo Applications starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause
"""
            script_path = self.project_root / "start_dev.bat"
        else:
            start_dev_content = """#!/bin/bash
echo "Starting RideShare Connect in Development Mode..."

# Start backend
echo ""
echo "Starting Backend..."
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# Wait a moment
sleep 3

# Start frontend
echo ""
echo "Starting Frontend..."
cd frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "Applications started!"
echo "Backend: http://localhost:5000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "Press Ctrl+C to stop both applications"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
"""
            script_path = self.project_root / "start_dev.sh"
            
        with open(script_path, "w") as f:
            f.write(start_dev_content)
            
        if sys.platform != "win32":
            os.chmod(script_path, 0o755)
            
        print("✓ Created development startup script")
        
    def setup_complete(self):
        """Display setup completion message"""
        print("\n" + "="*60)
        print("🎉 RideShare Connect Setup Complete!")
        print("="*60)
        
        print("\n📁 Project Structure:")
        print("├── app.py                 # Main Flask application")
        print("├── utils/                 # Bitcoin and utility modules")
        print("├── routes/                # API route blueprints")
        print("├── tests/                 # Test files")
        print("├── frontend/              # React application")
        print("├── docs/                  # Documentation")
        print("└── .env                   # Environment variables")
        
        print("\n🚀 Next Steps:")
        print("1. Update .env file with your Bitcoin RPC credentials")
        print("2. Initialize database: python init_db.py")
        print("3. Start development servers:")
        if sys.platform == "win32":
            print("   - Run: start_dev.bat")
        else:
            print("   - Run: ./start_dev.sh")
        print("4. Visit: http://localhost:3000")
        
        print("\n🔗 Useful Commands:")
        print("Backend:")
        print("  - source venv/bin/activate  # Activate virtual environment")
        print("  - python app.py            # Start Flask server")
        print("  - python -m pytest        # Run tests")
        
        print("\nFrontend:")
        print("  - cd frontend && npm start      # Start React dev server")
        print("  - cd frontend && npm test       # Run tests")
        print("  - cd frontend && npm run build  # Build for production")
        
        print("\n📚 Documentation:")
        print("  - README.md          # Main documentation")
        print("  - docs/API.md        # API documentation")
        
        print("\n💰 Bitcoin Integration:")
        print("  - Configure Bitcoin RPC in .env")
        print("  - Endpoints available at /api/bitcoin/*")
        print("  - Lightning Network support included")
        
        print(f"\n✨ Happy coding! Your RideShare Connect project is ready.")
        
    def run_setup(self):
        """Run complete setup process"""
        try:
            self.create_directory_structure()
            self.generate_env_file()
            self.setup_python_backend()
            self.setup_react_frontend()
            self.create_package_json_scripts()
            self.create_database_init_script()
            self.create_test_files()
            self.create_deployment_configs()
            self.create_readme_and_docs()
            self.run_initial_tests()
            self.create_startup_scripts()
            self.setup_complete()
            
        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            print("Please check the error and try again.")
            sys.exit(1)

if __name__ == "__main__":
    setup = RideShareSetup()
    setup.run_setup()