# Translative Research Assistant - RAG applicationd

RAG (Retrieval-Augmented Generation) based TRA research, using Pinecone and OpenAI's API.

Research article was published on IEEE AIxHEART 2024 proceedings [[cite](https://ieeexplore.ieee.org/document/10833972)]

## Setup

1. Create a virtual environment and install the required packages:

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

2. Create a free Pinecone account and get your API key from [here](https://www.pinecone.io/).

3. Create a `.env` file with the following variables:

```bash
OPENAI_API_KEY = [ENTER YOUR OPENAI API KEY HERE]
PINECONE_API_KEY = [ENTER YOUR PINECONE API KEY HERE]
PINECONE_API_ENV = [ENTER YOUR PINECONE API ENVIRONMENT HERE]
```
