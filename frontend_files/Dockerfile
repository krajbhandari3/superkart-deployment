# ------------------------------------------------------------
# Docker image for the SuperKart Streamlit frontend
# ------------------------------------------------------------

# Same small official Python base image as the backend
FROM python:3.12-slim

# Working folder inside the container
WORKDIR /app

# Install dependencies first (cached layer - faster rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app into /app
COPY . .

# Streamlit's default port
EXPOSE 8501

# Start Streamlit:
# --server.port=8501              -> port the UI listens on
# --server.address=0.0.0.0        -> accept connections from outside the container
# --server.enableCORS=false       -> allow access through the Codespace forwarded URL
# --server.enableXsrfProtection=false -> required for file uploads to work through
#                                    the Codespace proxy (otherwise batch upload fails with a 403 error)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
