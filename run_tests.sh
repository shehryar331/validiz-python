#!/bin/bash

# Run the unit tests
echo "Running unit tests..."
python -m pytest tests/unit -v

# Run the integration tests if VALIDIZ_API_KEY is set
if [ -n "$VALIDIZ_API_KEY" ]; then
    echo "Running integration tests..."
    python -m pytest tests/integration -v
else
    echo "Skipping integration tests (VALIDIZ_API_KEY not set)"
fi

# Run tests with coverage if requested
if [ "$1" == "--coverage" ]; then
    echo "Running tests with coverage..."
    python -m pytest --cov=validiz tests/
    
    # Generate HTML coverage report
    python -m pytest --cov=validiz --cov-report=html tests/
    echo "Coverage report generated in htmlcov/"
fi 