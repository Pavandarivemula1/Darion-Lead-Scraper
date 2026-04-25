# Use the official Microsoft Playwright image specifically designed for Python.
# This prevents ALL the usual headache of trying to manually install Chromium libraries on Linux.
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies normally (Playwright is already installed natively in this base image)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose a default port (Render will dynamically assign one via the $PORT env variable, but this is a fallback)
EXPOSE 10000

# Start the FastAPI server and carefully bind it to 0.0.0.0 so Render's proxy can access it
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-10000}"]
