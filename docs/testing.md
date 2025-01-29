# Testing Documentation

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Continuous Integration](#continuous-integration)
5. [Writing Tests](#writing-tests)
6. [Best Practices](#best-practices)
7. [Laptop Deployment Testing](#laptop-deployment-testing)

## Overview

Our testing suite consists of multiple test categories:

- Unit Tests: Testing individual components
- Integration Tests: Testing component interactions
- System Tests: Testing the entire application
- UI Tests: Testing user interface components
- Performance Tests: Testing system performance
- Network Tests: Testing network-dependent features
- Voice Tests: Testing voice input/output features

## Test Structure

```plaintext
tests/
├── unit/                 # Unit tests
│   ├── test_nlp.py      # Natural Language Processing tests
│   ├── test_voice.py    # Voice activation tests
│   ├── test_ai_providers.py  # AI provider tests
│   ├── test_ui.py       # UI component tests
│   └── test_ml.py       # Machine Learning tests
├── integration/         # Integration tests
│   └── test_component_integration.py
├── system/             # System tests
│   └── test_system.py
├── performance/        # Performance tests
│   └── test_benchmarks.py
└── ui/                 # UI tests
    └── test_monitoring_dashboard.py
```

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements-dev.txt
```
2. Set up environment variables:
```bash
cp .env.template .env
# Edit .env with your configuration
```

### Running Different Test Suites

1. **All Tests**
```bash
pytest
```
2. **Unit Tests**
```bash
pytest -m "unit"
```
3. **Integration Tests**
```bash
pytest -m "integration"
```
4. **System Tests**
```bash
pytest -m "system"
```
5. **UI Tests**
```bash
pytest -m "ui"
```
6. **Performance Tests**
```bash
pytest -m "performance"
```

### Test Options

- Run tests in parallel:
```bash
pytest -n auto
```
- Generate coverage report:
```bash
pytest --cov=src --cov-report=html
```
- Run specific test categories:
```bash
# Basic categories
pytest -m "unit"
pytest -m "integration"
pytest -m "system"
pytest -m "ui"
pytest -m "performance"

# Special categories
pytest -m "network"  # Network-dependent tests
pytest -m "voice"    # Voice input/output tests
pytest -m "gpu"      # GPU-dependent tests
pytest -m "memory"   # Memory monitoring tests

# Test speed categories
pytest -m "slow"     # Tests that take longer than 1 second
pytest -m "quick"    # Tests that complete quickly
```
- Skip certain test categories:
```bash
pytest -m "not slow"  # Skip slow tests
pytest -m "not network"  # Skip network tests
pytest -m "not gpu"  # Skip GPU tests
```
- Combine markers:
```bash
pytest -m "unit and not slow"  # Run fast unit tests only
pytest -m "performance and not network"  # Run offline performance tests
```

## Continuous Integration

Our CI pipeline runs automatically on:

- Every push to main/develop
- Every pull request
- Daily at midnight UTC

### CI Features

1. **Test Matrix**
- Multiple Python versions (3.8, 3.9, 3.10)
- Multiple OS (Ubuntu, Windows)

2. **Code Quality**
- Linting (flake8, black, isort, mypy, pylint)
- Coverage reporting (minimum 80% required)
- Performance benchmarking

3. **Security**
- Dependency scanning
- Code security analysis
- Vulnerability checking

### Viewing CI Results

1. Access GitHub Actions dashboard
2. Check test reports in PR comments
3. View coverage reports on Codecov
4. Download artifacts for detailed analysis

## Writing Tests

### Test Categories

1. **Unit Tests**
```python
@pytest.mark.unit
def test_function():
    assert function() == expected_result
```
2. **Integration Tests**
```python
@pytest.mark.integration
def test_component_interaction():
    result = component_a.interact_with(component_b)
    assert result.is_valid()
```
3. **System Tests**
```python
@pytest.mark.system
def test_full_workflow():
    app = Application()
    result = app.run_workflow()
    assert result.status == "success"
```
4. **UI Tests**
```python
@pytest.mark.ui
def test_button_click():
    button = find_element_by_id("submit")
    button.click()
    assert button.get_attribute("disabled")
```
5. **Performance Tests**
```python
@pytest.mark.performance
def test_response_time():
    start = time.time()
    result = function()
    duration = time.time() - start
    assert duration < 1.0  # seconds
```
6. **Network Tests**
```python
@pytest.mark.network
def test_api_call():
    response = api.get("/endpoint")
    assert response.status_code == 200
```
7. **Voice Tests**
```python
@pytest.mark.voice
def test_voice_recognition():
    audio = load_test_audio()
    text = voice_recognizer.transcribe(audio)
    assert "expected phrase" in text.lower()
```
8. **Memory Tests**
```python
@pytest.mark.memory
def test_memory_usage():
    tracker = MemoryTracker()
    with tracker.track():
        result = memory_intensive_function()
    assert tracker.peak_usage < 100_000_000  # bytes

### Using Fixtures

```python
@pytest.fixture
def test_data():
    """Provide test data for tests"""
    return {
        "id": 1,
        "name": "Test Item",
        "value": 100
    }

def test_processing(test_data):
    result = process_item(test_data)
    assert result["processed"] == True
```

### Mocking

```python
@patch('module.external_api')
def test_api_interaction(mock_api):
    mock_api.get.return_value = {"status": "success"}
    result = my_function()
    assert result.is_successful()
```

### Error Testing

```python
def test_error_handling():
    with pytest.raises(ValueError):
        function_that_should_raise()
```

## Best Practices

1. **Test Isolation**

- Each test should be independent
- Use fixtures for setup/teardown
- Mock external dependencies

2. **Naming Conventions**

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

3. **Coverage**

- Aim for 80% minimum coverage
- Focus on critical paths
- Document uncovered sections

4. **Performance**

- Keep tests fast
- Use parallel execution
- Mark slow tests with `@pytest.mark.slow`

5. **Documentation**

- Document test purpose
- Include example usage
- Explain complex test scenarios

6. **Environment Handling**

- Use environment variables for configuration
- Document required environment variables
- Provide sensible defaults when possible

7. **Error Handling**

- Test both success and failure cases
- Verify error messages
- Test edge cases

8. **Resource Management**

- Clean up resources after tests
- Use context managers
- Handle timeouts appropriately

## Laptop Deployment Testing

### System Requirements

- Windows 10 or later
- 8GB RAM minimum (16GB recommended)
- 2GB free disk space
- Internet connection

### Quick Start Guide

1. **Clone the Repository**
```bash
git clone [repository-url]
cd Head-AI
```

2. **Set Up Python Environment**
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment Variables**
```bash
# Copy the example environment file
copy .env.example .env
```
Then edit `.env` with your API keys:
- OpenAI API key
- Cohere API key
- Other required API keys

4. **Run Initial Setup**
```bash
# Run the setup script
.\setup.bat
```

5. **Start the Application**
```bash
# Run the assistant
.\run_assistant.bat
```

### Installation Options

### Option 1: Installer Package (Recommended)

1. Download `HeadAI_Setup.exe`
2. Run the installer
3. Follow the installation wizard
4. The setup will automatically:
   - Install required components
   - Create necessary directories
   - Set up the environment

### Option 2: Manual Installation

1. Download `HeadAI_Manual.zip`
2. Extract to your preferred location
3. Run `setup.bat`
4. Configure `.env` file with your API keys

### Testing Checklist

#### Basic Functionality
- [ ] Application starts without errors
- [ ] UI loads properly
- [ ] Can input text/commands
- [ ] Receives responses from AI
- [ ] Basic research functions work

#### Research Capabilities
- [ ] Web search works
- [ ] Can process search results
- [ ] Information synthesis works
- [ ] Can save research results

#### Memory System
- [ ] Remembers context between sessions
- [ ] Can access previous conversations
- [ ] Maintains user preferences

### Common Issues & Solutions

#### Installation Issues
1. **Python Version Mismatch**
   - Solution: Ensure Python 3.8+ is installed and in PATH

2. **Package Installation Errors**
   - Solution: Try running:
     ```bash
     pip install --upgrade pip
     pip install -r requirements.txt --no-cache-dir
     ```

3. **Environment Variable Issues**
   - Solution: Check `.env` file exists and contains valid API keys

#### Runtime Issues
1. **AI Provider Errors**
   - Check API key validity
   - Verify internet connection
   - Check API rate limits

2. **Memory/Performance Issues**
   - Close other resource-intensive applications
   - Clear application cache
   - Restart the application

### Reporting Issues

When reporting issues, please include:
1. Error message/screenshot
2. Steps to reproduce
3. System information
4. Log files (located in `./logs`)

### Testing Environment Setup

#### Development Environment
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

#### Production Environment
```bash
# Use production settings
copy .env.production .env
.\setup_complete.bat
```

### Performance Monitoring

Monitor system performance in:
- `./monitoring/` - System metrics
- `./performance/` - Performance logs
- `./analytics/` - Usage analytics

### Security Notes

- Never share API keys
- Keep `.env` file secure
- Regular security updates
- Monitor API usage

### Next Steps

After testing:
1. Report any issues
2. Provide feedback
3. Suggest improvements
4. Share performance metrics

### Support

For support:
1. Check documentation in `./docs/`
2. Review common issues above
3. Submit detailed bug reports
4. Contact development team

### Version Information

Track your version:
```bash
python -c "import src; print(src.__version__)"
```

Keep system updated:
```bash
git pull
pip install -r requirements.txt

```
