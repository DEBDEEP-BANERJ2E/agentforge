#!/bin/bash

# Start AgentForge FastAPI Backend
# This script activates the Conda environment and starts the API server

echo "=========================================="
echo "Starting AgentForge API Server"
echo "=========================================="

# Check if Conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: Conda not found. Please install Miniconda or Anaconda."
    exit 1
fi

# Activate Conda environment
echo "Activating Conda environment 'watsonx'..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate watsonx

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate Conda environment 'watsonx'"
    echo "Please run: conda env create -f backend/environment.yml"
    exit 1
fi

# Check if Orchestrate is configured
echo "Checking Orchestrate configuration..."
if ! command -v orchestrate &> /dev/null; then
    echo "Warning: Orchestrate CLI not found in PATH"
    echo "Make sure ibm-watsonx-orchestrate is installed"
fi

# Start the API server
echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

cd api
python main.py

# Made with Bob
