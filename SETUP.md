# EVE Map Visualization - Setup Guide

Complete installation and setup instructions for the EVE Map Visualization project.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Setup](#quick-setup)
- [Frontend Visualization Setup](#frontend-visualization-setup)
- [Backend API Setup](#backend-api-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Python**: 3.9 or higher
- **pip**: Latest version (upgrade with `pip install --upgrade pip`)
- **Git**: For cloning the repository
- **Virtual Environment**: Recommended for dependency isolation

### Operating System Support
- ✅ Linux (Ubuntu 20.04+, Debian, Fedora, etc.)
- ✅ macOS (10.15+)
- ✅ Windows 10/11

## Quick Setup

For users who want to get started quickly:

```bash
# Clone the repository
git clone https://github.com/AreteDriver/evemap.git
cd evemap

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
cd backend
pip install -r requirements.txt
cd ..

# Run example visualization
python examples/test_mock_data.py
```

## Frontend Visualization Setup

The frontend visualization component uses matplotlib and NetworkX for rendering 2D maps of EVE Online's New Eden.

### Step 1: Clone Repository

```bash
git clone https://github.com/AreteDriver/evemap.git
cd evemap
```

### Step 2: Create Virtual Environment

Using a virtual environment is recommended to avoid dependency conflicts.

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows Command Prompt:
.venv\Scripts\activate.bat

# On Windows PowerShell:
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Dependencies Installed:
- `requests>=2.31.0` - HTTP library for ESI API calls
- `matplotlib>=3.8.0` - 2D plotting and visualization
- `networkx>=3.2.0` - Graph algorithms and layouts
- `pandas>=2.0.0` - Data manipulation (if needed)
- `numpy>=1.24.0` - Numerical computing

### Step 4: Verify Installation

```bash
python -c "from evemap import ESIClient, NedenMap; print('Frontend setup successful!')"
```

### Step 5: Run Example

```bash
# Run the test mock data example
python examples/test_mock_data.py

# This will create a test map at examples/test_mock_map.png
```

## Backend API Setup

The backend is a FastAPI application providing RESTful endpoints for system queries and route calculation.

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Backend Virtual Environment

It's recommended to use a separate virtual environment for the backend:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows Command Prompt:
.venv\Scripts\activate.bat

# On Windows PowerShell:
.venv\Scripts\Activate.ps1
```

### Step 3: Install Backend Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Backend Dependencies:
- `fastapi>=0.109.1,<0.110.0` - Modern web framework
- `uvicorn[standard]>=0.15.0,<0.24.0` - ASGI server
- `pydantic>=1.10,<2.0` - Data validation (v1.x for compatibility)
- `httpx>=0.23.0,<0.24.0` - Async HTTP client
- `python-multipart` - Form data parsing

### Step 4: Verify Backend Installation

```bash
# Run verification script
python verify.py

# Run backend tests
python test_backend.py
```

### Step 5: Start the Backend Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Root**: http://localhost:8000
- **Interactive Swagger UI**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Verification

### Test Frontend Visualization

```bash
# Make sure you're in the project root with frontend venv activated
cd /path/to/evemap
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Run test example
python examples/test_mock_data.py

# Check that the output file was created
ls examples/test_mock_map.png
```

### Test Backend API

```bash
# Make sure backend server is running
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

In another terminal:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected output: {"status":"healthy"}

# Test systems list
curl http://localhost:8000/systems/

# Test risk report
curl http://localhost:8000/systems/Jita/risk

# Test route calculation
curl "http://localhost:8000/map/route?from=Jita&to=Niarja&profile=safer"
```

### Run All Tests

```bash
# Frontend tests (from project root)
python -m pytest tests/

# Backend tests (from backend directory)
cd backend
python test_backend.py
python verify.py
```

## Configuration

### Customize Universe Data

Edit `backend/app/data/universe.json` to add or modify systems:

```json
{
  "systems": {
    "YourSystem": {
      "name": "YourSystem",
      "security_status": 0.5,
      "region": "YourRegion",
      "constellation": "YourConstellation"
    }
  },
  "gates": [
    {
      "from_system": "YourSystem",
      "to_system": "Jita",
      "distance": 1.0
    }
  ]
}
```

### Customize Risk Profiles

Edit `backend/app/data/risk_config.json` to adjust risk calculations:

```json
{
  "weights": {
    "security_weight": 0.6,
    "zkill_weight": 0.4
  },
  "profiles": {
    "custom": {
      "risk_multiplier": 3.0,
      "max_acceptable_risk": 30
    }
  }
}
```

## Troubleshooting

### Common Issues

#### Issue: Import errors when running examples

**Solution**: Make sure you're in the correct directory and virtual environment is activated:
```bash
cd /path/to/evemap
source .venv/bin/activate  # Linux/macOS
python examples/test_mock_data.py
```

#### Issue: ModuleNotFoundError for 'evemap'

**Solution**: Install the package in development mode:
```bash
pip install -e .
```

#### Issue: Matplotlib doesn't display on headless systems

**Solution**: Use a non-interactive backend:
```python
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
```

Or set environment variable:
```bash
export MPLBACKEND=Agg
```

#### Issue: FastAPI/Uvicorn import errors

**Solution**: Ensure you're in the backend directory with backend venv activated:
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

#### Issue: Port 8000 already in use

**Solution**: Use a different port:
```bash
uvicorn app.main:app --port 8080
```

#### Issue: Permission denied when activating virtual environment on Windows

**Solution**: Change PowerShell execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Version Issues

If you encounter type annotation errors, ensure you're using Python 3.9+:

```bash
python --version
# Should show Python 3.9.x or higher
```

To use a specific Python version:
```bash
python3.9 -m venv .venv
```

### Dependency Conflicts

If you experience dependency conflicts:

```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## Advanced Setup

### Development Installation

For contributors who want to modify the code:

```bash
# Install in editable mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### Docker Setup (Optional)

Create a `Dockerfile` for the backend:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t evemap-backend .
docker run -p 8000:8000 evemap-backend
```

### Environment Variables

You can configure the backend using environment variables:

```bash
# Set project name
export PROJECT_NAME="EVE Map API"

# Set API version
export API_VERSION="1.0.0"

# Start server
uvicorn app.main:app --reload
```

## Next Steps

After successful setup:

1. **Explore the Examples**: Check the `examples/` directory for usage patterns
2. **Read the API Documentation**: Visit http://localhost:8000/docs when the backend is running
3. **Customize Configurations**: Modify `universe.json` and `risk_config.json` for your needs
4. **Review Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
5. **Start Building**: Use the API and visualization tools in your own projects

## Getting Help

- **Documentation**: Check [README.md](README.md) for feature overview
- **Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- **Issues**: Report problems on GitHub Issues
- **Examples**: Review code in `examples/` directory

---

Happy mapping! 🚀
