# 🤖 MATBOT

## SUMMARY 
**MATBOT** is an **AI-powered troubleshooter** for **MATLAB-related issues**. Designed with a **streamlit** interface, it helps users get quick and accurate solutions to their MATLAB queries by leveraging state-of-the-art **retrieval-augmented generation** (RAG) techniques.

## 🔧 Features
- 💬 **Interactive UI** built using **Streamlit** for a chat-based experience.

- 🔍 **Context-aware** responses powered by LangChain and Chroma vector store.

- 🧠 Deep Learning Support using **HuggingFace Transformers and PyTorch.**

- 🧪 Uses **RAG** (Retrieval-Augmented Generation) for precise and relevant answers.

- 📚 Integrates Wikipedia and **web search** via Tavily for enhanced context.

- 🧮 Calculates confidence with **cosine similarity** from sklearn.metrics.pairwise.

## 🛠️ Tech Stack
- 🐍 **Python :**  The core programming language used for MATBOT. Python is ideal for AI/ML projects because of its rich ecosystem of libraries and frameworks.
#####


- 🧠 **LangChain :**  LangChain helps structure and manage RAG (Retrieval-Augmented Generation) pipelines. It allows you to combine LLMs with external sources like vector databases, tools, or APIs .
#####


- 🤗 **HuggingFace Transformers :** This library is used to load and run powerful pretrained language models (like Mistral-7B) and embedding models (like BAAI/bge). 
#####


- 🗃️ **Chroma (Vector Store) :** Chroma is a vector database where the project stores document embeddings. 
#####


- 🔥 **PyTorch :** PyTorch is the underlying deep learning framework used to run the Mistral-7B model and the embedding model on the GPU.
#####
- 📊 **scikit-learn :** Used for computing cosine similarity between the query vector and document vectors and helps determine the confidence score .
#####


- 🌐 **Streamlit :** A Python-based web framework for building interactive user interfaces. Streamlit is used to build the frontend of MATBOT where users can enter queries and view responses easily.
#####


- 🔍 **Tavily API :** Used to pull real-time web search results when the internal documentation is insufficient. 


## 🚀 How It Works
- User inputs a MATLAB-related question via the Streamlit UI.

- The query is embedded and compared against a preloaded document database using Chroma.

- If needed, it fetches additional context from Wikipedia and the web.

- A well-structured prompt is created and sent to a language model (e.g., Mistral or similar).

- The model generates a step-by-step, technically accurate response.

## How to Run

1. Clone the repository.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run the app:
   ```bash
   streamlit run app.py

## 🌐 Deployment
The MATBOT website is live and replicates the ChatGPT experience. Users can chat with the bot and receive MATLAB troubleshooting advice in real time.


![MATBOT Interface](Rough/images/login.png)


![MATBOT Interface](Rough/images/page_1.png)




## 🎨 Design Choices and Results
- **Lightweight Frontend:** Streamlit was chosen for its rapid prototyping capability and ease of use.

- **Model Selection:** Mistral-7B was selected for its balance between performance and resource efficiency. BAAI/bge embeddings proved to be robust in capturing query-document similarity.

- **Chroma DB:** Enabled scalable, low-latency retrieval across varied documentation sets.

- **Fallback Strategy:** Tavily API ensures broader coverage by pulling from real-time web data.



## 🧪Results:

- Achieved 85–90% accuracy on internal benchmarks.

- Average response latency ~2.5–3 seconds.

- Positive feedback in pilot tests with MATLAB users (both students and researchers).


   

## 📁 Project Structure


**MATBOT/**
├── data/
├── Embed-5/
├── Embed-all
├── Embed-all-Act
├── images/
├── mat/
├── MatBot/
├── Rough/
├── .env/
├── .gitignore/
├── newapp.py/
├── nlp.py
└── README.md


