#!/bin/bash

# Test runner script for the FastAPI application

echo "Running FastAPI tests..."
echo "=========================="

# Activate the conda environment and run tests
conda activate copilotreview
python -m pytest tests/ -v --cov=src --cov-report=term-missing

echo ""
echo "Tests completed!"