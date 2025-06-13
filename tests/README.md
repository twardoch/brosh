# Brosh Tests

This directory contains comprehensive tests for the brosh package.

## Test Structure

### Test Files

- `conftest.py` - Pytest configuration and shared fixtures
- `test_package.py` - Basic package tests (version, imports)
- `test_models.py` - Tests for data models and enums
- `test_api.py` - Tests for the public API functions
- `test_cli.py` - Tests for the CLI interface
- `test_browser.py` - Tests for browser management utilities

### Test Categories

- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Test interactions between components
- **API Tests**: Test the public API interface
- **CLI Tests**: Test command-line interface functionality

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -e ".[test]"
```

### Running All Tests

```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py

# Using pytest with coverage
pytest --cov=src/brosh --cov-report=html
```

### Running Specific Tests

```bash
# Run tests for a specific module
pytest tests/test_models.py

# Run tests for a specific class
pytest tests/test_models.py::TestImageFormat

# Run tests for a specific function
pytest tests/test_models.py::TestImageFormat::test_mime_type_property

# Run tests matching a pattern
pytest -k "test_capture"

# Run only unit tests (if marked)
pytest -m "unit"

# Run only async tests
pytest -m "asyncio"
```

### Test Options

```bash
# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run in parallel (if pytest-xdist is installed)
pytest -n auto

# Show coverage report
pytest --cov=src/brosh --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src/brosh --cov-report=html
```

## Test Coverage

The tests aim for high coverage of the brosh codebase:

- **Models**: Complete coverage of data models, validation, and enums
- **API**: Coverage of all public API functions and error handling
- **CLI**: Coverage of command-line interface and option parsing
- **Browser Management**: Coverage of browser detection and management
- **Error Handling**: Tests for various error conditions and edge cases

## Test Configuration

Test configuration is defined in `pyproject.toml`:

- Test discovery patterns
- Coverage settings
- Async test configuration
- Warning filters
- Markers for test categorization

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `temp_output_dir`: Temporary directory for test outputs
- `sample_url`: Sample URL for testing
- `sample_capture_config`: Sample configuration objects
- Mock objects for Playwright browser components

## Mocking Strategy

Tests use mocking to isolate units under test:

- **Browser interactions**: Mock Playwright browser, context, and page objects
- **File system operations**: Mock file I/O where appropriate
- **External processes**: Mock subprocess calls for browser launching
- **Network requests**: Mock HTTP requests and responses

## CI/CD Integration

Tests are configured for continuous integration:

- Coverage reports in XML format for CI systems
- Proper exit codes for build success/failure
- Parallel test execution support
- Configurable warning filters

## Adding New Tests

When adding new tests:

1. Follow the existing naming conventions (`test_*.py`)
2. Use appropriate fixtures from `conftest.py`
3. Mock external dependencies
4. Test both success and error cases
5. Add docstrings explaining what each test validates
6. Use appropriate test markers if needed

### Test Naming

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>_<condition>`

### Example Test Structure

```python
class TestFeature:
    """Test the Feature class."""

    def test_feature_creation_success(self) -> None:
        """Test successful feature creation."""
        # Arrange
        # Act
        # Assert

    def test_feature_creation_invalid_input(self) -> None:
        """Test feature creation with invalid input."""
        # Test error conditions
        with pytest.raises(ValueError):
            # Test code that should raise ValueError

    @pytest.mark.asyncio
    async def test_feature_async_operation(self) -> None:
        """Test async feature operation."""
        # Test async functionality
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the package is installed in development mode
2. **Async Test Failures**: Make sure pytest-asyncio is installed
3. **Coverage Issues**: Check that the source paths are correct
4. **Mock Failures**: Verify mock patches target the correct module paths

### Debug Mode

Run tests with debug output:

```bash
pytest -v -s --tb=long
```

Add debugging breakpoints in tests:

```python
import pdb; pdb.set_trace()
```

Or use pytest's built-in debugging:

```bash
pytest --pdb
```
