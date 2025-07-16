#!/bin/bash
# Script to fix code formatting issues

echo "=== Fixing Code Formatting ==="

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install formatting tools
echo "Installing formatting tools..."
pip install black isort flake8

# Run Black to format all Python files
echo "Running Black formatter..."
black app/ tests/

# Run isort to sort imports
echo "Running isort..."
isort app/ tests/

# Check with flake8 (this will show remaining issues if any)
echo "Checking with flake8..."
flake8 app/ --max-line-length=100 --extend-ignore=E203,W503 || true

echo ""
echo "=== Formatting Complete ==="
echo "Don't forget to commit the changes:"
echo "  git add ."
echo "  git commit -m 'Fix code formatting with Black and isort'"
echo "  git push"