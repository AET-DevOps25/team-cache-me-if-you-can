# StudySync AI Service

This service provides the AI-powered features for the StudySync platform, including a RAG-based chat assistant trained on uploaded course materials.

## Features

- **AI Chat Assistant**: Answers questions based on uploaded documents using a RAG pipeline.
- **Document Processing**: Extracts text from uploaded files (PDFs, Slides) and indexes them in a vector store.
- **Searchable Knowledge Base**: Leverages Weaviate for efficient semantic search over documents.

## Tech Stack

- **Python 3.10+**
- **Framework**: FastAPI
- **AI/ML**: LangChain, OpenAI (or other LLMs like GPT4All)
- **Vector Database**: Weaviate
- **Containerization**: Docker

## Project Structure

```
ai_service/
├── app/                      # Main application source code
│   ├── api/                  # API layer (FastAPI endpoints)
│   ├── core/                 # Core AI logic (RAG, LLM interaction)
│   ├── document_handling/    # Document parsing and text extraction
│   ├── models/               # Pydantic models for API validation
│   ├── services/             # Business logic layer
│   ├── vector_store/         # Weaviate client and interaction logic
│   ├── utils/                # Utility functions
│   ├── config.py             # Application configuration
│   └── main.py               # FastAPI application entry point
├── tests/                    # Automated tests
├── scripts/                  # Utility scripts
├── notebooks/                # Jupyter notebooks for experimentation
├── .env.example              # Example environment variables
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

## Setup and Running

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Copy `.env.example` to `.env` and fill in the required values (e.g., API keys, database URLs).
    ```bash
    cp .env.example .env
    # nano .env or code .env
    ```

4.  **Run the FastAPI application:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The API will be accessible at `http://localhost:8000` and Swagger docs at `http://localhost:8000/docs`.

5.  **Running with Docker:**
    ```bash
    # Build the Docker image
    docker build -t studysync-ai-service .

    # Run the Docker container
    docker run -p 8000:8000 --env-file .env studysync-ai-service
    ```

## API Endpoints

(To be detailed here once implemented)

-   `POST /api/v1/chat`: Send a query to the AI assistant.
-   `POST /api/v1/documents`: Upload a document for processing and indexing.
-   `GET /api/v1/documents/{document_id}`: Retrieve document status or information.

## Interacting with Spring Boot Backend

This AI service will expose RESTful APIs that the Spring Boot backend can call. Communication should ideally be asynchronous where appropriate.
Authentication between services can be handled using API keys or a token-based mechanism (e.g., JWT passed from the main backend).

## Weaviate Integration

The service connects to a Weaviate instance for:
-   Storing document embeddings.
-   Performing semantic searches to retrieve relevant context for the RAG pipeline.

Configuration for Weaviate (URL, API key if applicable) is managed via environment variables. 