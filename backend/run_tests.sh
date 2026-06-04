#!/bin/bash

# Script to run tests for FitVision backend

echo "Running FitVision Backend Tests..."
echo "================================="

# Install test dependencies if not already installed
pip install -r requirements-test.txt

# Run tests with coverage
echo "Running unit tests with coverage..."
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

# Run specific test categories
if [ "$1" = "unit" ]; then
    echo "Running only unit tests..."
    pytest tests/models tests/repositories tests/services -v
elif [ "$1" = "integration" ]; then
    echo "Running only integration tests..."
    pytest tests/routes -v
elif [ "$1" = "fast" ]; then
    echo "Running fast tests (excluding slow tests)..."
    pytest -m "not slow" -v
fi

echo "================================="
echo "Test run complete!"
echo "Coverage report available in htmlcov/index.html"