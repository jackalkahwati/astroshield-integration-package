#!/bin/bash

# Run all tests for the UDL integration package

# Enable exit on error
set -e

echo "Running UDL Integration tests..."

# Determine the project root directory
PROJECT_ROOT=$(git rev-parse --show-toplevel)
if [ -z "$PROJECT_ROOT" ]; then
  # Fallback if not in a git repository
  PROJECT_ROOT=$(cd "$(dirname "$0")/../../../../" && pwd)
fi

# Navigate to the project root
cd "$PROJECT_ROOT"

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e .
pip install pytest pytest-cov

# Run tests
echo "Running tests with coverage..."
pytest --cov=src/asttroshield/udl_integration src/asttroshield/udl_integration/tests/

# Deactivate virtual environment
deactivate

echo "Tests completed!" 