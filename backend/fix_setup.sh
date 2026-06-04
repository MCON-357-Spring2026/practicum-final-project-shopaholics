#!/bin/bash

# Script to fix the backend setup and run the server

echo "Fixing FitVision Backend Setup..."
echo "================================="

# Create a new virtual environment
echo "Creating fresh virtual environment..."
python3 -m venv venv_new

# Activate the new virtual environment
source venv_new/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Load environment variables
echo "Loading environment variables..."
export $(grep -v '^#' .env | xargs)

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Start the development server
echo "Starting Flask development server..."
echo "================================="
echo "Server will run on http://localhost:5000"
flask run --host=0.0.0.0 --port=5000