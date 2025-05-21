from setuptools import setup, find_packages

setup(
    name="genai",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic-settings",
        "python-dotenv",
        "openai",
        "langchain",
        "langchain-openai",
        "langchain-weaviate",
        "langchain-text-splitters",
        "langchain-community",
        "weaviate-client",
    ],
) 