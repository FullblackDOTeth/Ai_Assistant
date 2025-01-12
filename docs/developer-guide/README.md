# Developer Guide

Welcome to the Head AI Developer Guide! This guide will help you understand the codebase and contribute effectively to the project.

## Table of Contents

1. [Development Environment](#development-environment)
2. [Code Structure](#code-structure)
3. [Development Workflow](#development-workflow)
4. [Testing](#testing)
5. [Documentation](#documentation)
6. [Best Practices](#best-practices)

## Development Environment

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git
- PostgreSQL 14+
- Redis 6+
- Visual Studio Code (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/head-ai.git
   cd head-ai
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate   # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

6. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```

### IDE Configuration

We recommend using Visual Studio Code with the following extensions:

- Python
- Pylance
- Docker
- YAML
- ESLint
- Prettier
- GitLens
- Remote Development

## Code Structure

The project follows a modular architecture:

```
head-ai/
├── src/                    # Main source code
│   ├── api/               # API endpoints
│   ├── core/              # Core business logic
│   ├── models/            # Data models and schemas
│   ├── services/          # Business services
│   ├── utils/             # Utility functions
│   └── main.py           # Application entry point
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── frontend/             # Frontend application
│   ├── src/              # Frontend source code
│   ├── public/           # Static assets
│   └── package.json      # Frontend dependencies
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── deployment/           # Deployment configurations
├── .github/              # GitHub configurations
└── README.md            # Project overview
```

### Key Components

1. **API Layer** (`src/api/`):
   - RESTful endpoints
   - Request/response handling
   - Input validation
   - Authentication/authorization

2. **Core Layer** (`src/core/`):
   - Business logic
   - Domain models
   - Configuration
   - Constants

3. **Services Layer** (`src/services/`):
   - External integrations
   - Database operations
   - Caching
   - Background tasks

4. **Models Layer** (`src/models/`):
   - Data models
   - Schemas
   - DTOs
   - Enums

## Development Workflow

1. **Branch Management**:
   - `main`: Production-ready code
   - `develop`: Development branch
   - Feature branches: `feature/feature-name`
   - Bug fixes: `fix/bug-name`
   - Releases: `release/version`

2. **Development Process**:
   ```bash
   # Create feature branch
   git checkout -b feature/new-feature

   # Make changes and commit
   git add .
   git commit -m "feat: add new feature"

   # Push changes
   git push origin feature/new-feature

   # Create pull request
   # Wait for review and CI checks
   ```

3. **Code Review Process**:
   - All changes require pull requests
   - At least one approval required
   - All tests must pass
   - Code coverage requirements met
   - Linting checks passed

4. **Commit Messages**:
   Follow conventional commits:
   ```
   feat: add new feature
   fix: resolve bug
   docs: update documentation
   test: add tests
   refactor: improve code structure
   ```

## Testing

1. **Unit Tests**:
   ```bash
   pytest tests/unit
   ```

2. **Integration Tests**:
   ```bash
   pytest tests/integration
   ```

3. **End-to-End Tests**:
   ```bash
   pytest tests/e2e
   ```

4. **Coverage Report**:
   ```bash
   pytest --cov=src tests/
   ```

## Documentation

1. **Code Documentation**:
   - Use docstrings for all public functions/classes
   - Follow Google Python Style Guide
   - Keep documentation up-to-date

2. **API Documentation**:
   - Update OpenAPI specification
   - Document all endpoints
   - Include request/response examples

3. **Architecture Documentation**:
   - Update diagrams
   - Document design decisions
   - Keep dependencies updated

## Best Practices

1. **Code Quality**:
   - Follow PEP 8
   - Use type hints
   - Write descriptive variable names
   - Keep functions small and focused

2. **Security**:
   - Never commit secrets
   - Validate all inputs
   - Follow security guidelines
   - Regular dependency updates

3. **Performance**:
   - Profile code regularly
   - Optimize database queries
   - Use caching appropriately
   - Monitor resource usage

4. **Error Handling**:
   - Use custom exceptions
   - Proper error messages
   - Consistent error responses
   - Logging for debugging

## Troubleshooting

Common issues and solutions:

1. **Database Connection**:
   ```bash
   # Check database status
   docker-compose ps
   # View logs
   docker-compose logs db
   ```

2. **Redis Connection**:
   ```bash
   # Check Redis status
   redis-cli ping
   # View logs
   docker-compose logs redis
   ```

3. **API Issues**:
   ```bash
   # Check logs
   tail -f logs/api.log
   # Run in debug mode
   python src/main.py --debug
   ```

## Support

For development support:

1. Check existing issues
2. Ask in #dev channel
3. Contact tech lead
4. Update documentation

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.
