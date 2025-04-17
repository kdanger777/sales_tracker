#!/bin/bash

# Create virtual environment named "sales_env"
echo "Creating virtual environment 'sales_env'..."
python3 -m venv sales_env

# Activate the virtual environment
echo "Activating virtual environment..."
source sales_env/.bin/activate 2>/dev/null || source sales_env/bin/activate

# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Show installed packages
echo "Installed packages:"
pip list

echo ""
echo "Virtual environment 'sales_env' setup complete!"
echo "To activate the environment, run: source sales_env/bin/activate"
echo "To deactivate the environment, run: deactivate"
