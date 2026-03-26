# Variables
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Create the virtual environment
setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

# Install dependencies
install: setup
	$(PIP) install -r requirements.txt

# Run your script (example)
run:
	$(PYTHON) main.py

# Clean up the environment
clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} 