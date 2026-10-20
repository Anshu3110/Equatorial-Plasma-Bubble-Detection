FROM python:3.10-slim

WORKDIR /app

# Copy requirements from backend directory
# Copy requirements from backend directory
COPY backend/requirements.txt .

# Install system dependencies for OpenCV and others
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libhdf5-dev \
    libnetcdf-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --timeout=300 --retries=5 -r requirements.txt

# Copy backend app
COPY backend/app/ ./app/

# Copy shared ML source code
COPY src/ ./src/

# Copy trained models
COPY models/ ./models/

# Create directories for data/results if they don't exist
RUN mkdir -p /app/data /app/results

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
