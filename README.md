# 🧠 Quiz AI

An intelligent quiz generation system that uses AI to create multiple-choice questions from any topic. The system combines semantic search, embeddings, and large language models to generate contextually relevant quizzes.

## Features

- **AI-Powered Quiz Generation**: Generate multiple-choice questions from any topic
- **Semantic Search**: Advanced text search using FAISS vector database
- **Embeddings**: State-of-the-art sentence embeddings for semantic understanding
- **Interactive UI**: User-friendly Streamlit-based frontend
- **FastAPI Backend**: Scalable REST API backend

## Project Structure

```
quiz-ai/
├── backend/              # FastAPI backend service
│   ├── main.py          # Main application entry point
│   └── services/        # Core service modules
│       ├── embedding_service.py    # Text embedding service
│       ├── faiss_service.py        # Vector database service
│       └── llm_service.py          # Language model service
├── frontend/            # Streamlit frontend application
│   └── app.py          # Main UI application
├── data/               # Data storage directory
└── venv/               # Virtual environment
```

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd quiz-ai
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn streamlit requests faiss-cpu sentence-transformers
   ```

## Running the Application

### Start the Backend Server

In a terminal, navigate to the project root and run:

```bash
uvicorn backend.main:app --reload --port 8000
```

The backend API will be available at `http://127.0.0.1:8000`

### Start the Frontend UI

In a new terminal, run:

```bash
streamlit run frontend/app.py
```

The frontend will open at `http://localhost:8501`

## API Endpoints

### Health Check
- **GET** `/health` - Check backend status

### Quiz Generation
- **POST** `/generate-quiz` - Generate quiz questions
  - Request body: `{"topic": "your_topic"}`
  - Returns: JSON with quiz questions and answers

### Text Search
- **POST** `/search` - Search for relevant texts
  - Request body: `{"query": "search_query"}`
  - Returns: Search results

### Text Addition
- **POST** `/add-text` - Add texts to the vector database
  - Request body: `{"texts": ["text1", "text2", ...]}`
  - Returns: Confirmation message

## Usage

1. Open the frontend application in your browser
2. Enter a quiz topic in the text input field
3. Click "Generate Quiz" to create questions
4. Answer the questions and click "Check Answer" to verify
5. View explanations for each answer

## Services Overview

### Embedding Service
Converts text into semantic embeddings using pre-trained sentence transformers. These embeddings capture the semantic meaning of text, enabling similarity-based search.

### FAISS Service
Manages a vector database for efficient similarity search. FAISS (Facebook AI Similarity Search) provides fast approximate nearest neighbor search in high-dimensional spaces.

### LLM Service
Interfaces with language models to generate quiz questions and explanations based on provided context.

## Technologies Used

- **FastAPI**: Modern Python web framework
- **Streamlit**: Quick data app framework for the frontend
- **FAISS**: Vector similarity search library
- **Sentence Transformers**: Pre-trained embedding models
- **Uvicorn**: ASGI web server

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]

## Support

For issues or questions, please open an issue on the repository or contact the development team.


flowchart TB

    %% USER LAYER
    U[👤 User]

    %% PRESENTATION LAYER
    UI[🖥️ Streamlit Frontend<br/>• PDF Upload<br/>• Topic Input<br/>• Difficulty Selector<br/>• Quiz UI]

    %% APPLICATION LAYER
    API[⚙️ FastAPI Backend]

    %% INGESTION PIPELINE
    PDF[📄 PDF Upload]
    EXTRACT[🧾 Text Extraction]
    CHUNK[✂️ Text Chunking]
    EMBED[🔢 Embedding Model<br/>(SentenceTransformer)]

    %% STORAGE
    VDB[(🧠 FAISS Vector DB)]

    %% RAG PIPELINE
    QUERY[🔍 Query Embedding]
    RETRIEVE[📌 Top-K Retrieval]
    PROMPT[🧩 Prompt Builder<br/>(Difficulty Aware)]

    %% LLM
    LLM[🤖 Local LLM<br/>(Ollama – Qwen / Llama)]

    %% OUTPUT
    QUIZ[📝 Structured Quiz JSON]
    EVAL[✅ Answer Validation<br/>+ Scoring]

    %% FLOW
    U --> UI
    UI --> API

    %% PDF Ingestion Flow
    UI --> PDF
    PDF --> API
    API --> EXTRACT
    EXTRACT --> CHUNK
    CHUNK --> EMBED
    EMBED --> VDB

    %% Quiz Generation Flow
    UI -->|Topic + Difficulty| API
    API --> QUERY
    QUERY --> VDB
    VDB --> RETRIEVE
    RETRIEVE --> PROMPT
    PROMPT --> LLM
    LLM --> QUIZ
    QUIZ --> API
    API --> UI

    %% Quiz Attempt Flow
    UI --> EVAL
    EVAL --> 
  