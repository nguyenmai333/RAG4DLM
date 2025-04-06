# RAG4DLM 🔍

> Building intelligent Retrieval-Augmented Generation (RAG) systems for enhanced document processing and knowledge retrieval.

## 🚀 Features

- Web crawling capabilities
- Document processing and indexing
- Interactive query interface
- Built-in RAG implementation

## 📦 Installation

First, create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_api_key_here
```

Then, install the required Python packages:


```bash
pip install -r requirements.txt
```

Then, set up the Playwright browser automation:

```bash
playwright install
```

## 🔧 Usage

The system consists of three main components:

1. **Data Collection**
```bash
python crawler.py 
```

2. **RAG Processing**
```bash
python ./LLM/rag.py
```

3. **Chatbot Interface**
```bash
streamlit run app.py
```

## 📝 License

MIT License

## 📬 Contact

For questions and feedback, please open an issue in the repository.