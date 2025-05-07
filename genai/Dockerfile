# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define environment variables (can be overridden at runtime)
# ENV OPENAI_API_KEY="your_openai_api_key"
# ENV WEAVIATE_URL="http://localhost:8080"

# Command to run the application using Uvicorn
# The app.main:app refers to the FastAPI application instance `app` in the `app/main.py` file.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 