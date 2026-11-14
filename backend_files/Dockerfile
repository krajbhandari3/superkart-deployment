# ------------------------------------------------------------
# Docker image for the SuperKart Flask backend
# ------------------------------------------------------------

# Start from a small official Python image (slim = fewer extras, smaller image)
FROM python:3.12-slim

# Set the working folder inside the container; all following commands run here
WORKDIR /app

# Copy ONLY requirements first, then install.
# Docker caches each step - if requirements don't change, rebuilds skip
# this slow install step even when app.py changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else (app.py, superkart_model.joblib) into /app
COPY . .

# Document that the container listens on port 7860
EXPOSE 7860

# Start the API with gunicorn (a production web server) instead of Flask's dev server.
# -w 2               -> 2 worker processes to handle requests in parallel
# -b 0.0.0.0:7860    -> listen on all network interfaces, port 7860
# app:superkart_api  -> file app.py, Flask object named superkart_api
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "app:superkart_api"]
