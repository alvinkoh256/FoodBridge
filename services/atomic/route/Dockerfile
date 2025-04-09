FROM python:3.11

WORKDIR /app

# Install build essentials and wheel
RUN pip install --upgrade pip setuptools wheel

# Copy requirements but skip the problematic package during installation
COPY requirements.txt .
RUN grep -v "googlemaps" requirements.txt > requirements_filtered.txt && \
    pip install --no-cache-dir -r requirements_filtered.txt

# Install googlemaps using pip install with specific flags
RUN pip install --no-cache-dir googlemaps --no-binary googlemaps

# Copy your application code
COPY . .

# Run your application
CMD ["python", "route.py"]