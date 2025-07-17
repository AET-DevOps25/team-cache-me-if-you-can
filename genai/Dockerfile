FROM python:3.10-slim

# Install system dependencies for pdf to image and latex
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    texlive-base \
    texlive-latex-base \
    texlive-fonts-recommended \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libsm6 \
    libxext6 \
    libxrender1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 