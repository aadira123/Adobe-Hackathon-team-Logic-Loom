
# Persona-Based Document Intelligence from PDFs

This project implements a document intelligence system that processes PDF documents, extracts relevant sections based on predefined "personas," and provides insights in a structured JSON format. It leverages Sentence Transformers for semantic similarity to match document content with the "job-to-be-done" of a selected persona.

---

## Features

* **PDF Text Extraction**: Extracts raw text content from PDF files.
* **Smart Text Chunking**: Splits large documents into manageable, overlapping text chunks to preserve context.
* **Semantic Search**: Uses state-of-the-art Sentence Transformer models (`all-MiniLM-L6-v2`) to embed document chunks and persona queries.
* **Persona-Driven Relevance**: Identifies and ranks document sections most relevant to a specific user persona's objectives ("job-to-be-done").
* **Structured JSON Output**: Generates a detailed JSON report including metadata, extracted relevant sections, and a subsection analysis.
* **Batch Processing**: Automatically processes all PDF files found in the designated input directory.
* **Dockerized Deployment**: Provides a `Dockerfile` for easy setup and consistent execution across different environments.

---

## How It Works

The core functionality revolves around semantic similarity:

1.  **PDF Parsing and Chunking**: The system first extracts all text from PDF documents and then divides this text into smaller, overlapping chunks. This ensures that context is maintained even when relevant information spans across sentences or paragraphs.
2.  **Persona Definition**: Predefined user personas (e.g., "Data Scientist", "PhD Researcher") are equipped with a `role`, `expertise`, and a `job_to_be_done` (a description of what they aim to achieve or find in the documents).
3.  **Semantic Embedding**: Both the persona's `job_to_be_done` and each document text chunk are converted into high-dimensional numerical vectors (embeddings) using a pre-trained Sentence Transformer model (`all-MiniLM-L6-v2`).
4.  **Similarity Calculation**: Cosine similarity is calculated between the persona's "job-to-be-done" embedding and every document chunk embedding.
5.  **Relevance Filtering and Ranking**: Chunks with a cosine similarity score above a configurable `THRESHOLD` are considered relevant. These relevant sections are then ranked by their similarity score.
6.  **JSON Output**: The results, including the identified relevant sections and a more detailed subsection analysis (the actual text chunks), are compiled into a comprehensive JSON file.

---

## Getting Started

### Prerequisites

* Python 3.8+
* pip (Python package installer)
* Docker (if you plan to use the Dockerized version)

### Local Setup and Execution

1.  **Clone the repository (or save the files):**
    Ensure `main.py` and `requirements.txt` are in your project's root directory.

    ```bash
    mkdir document-intelligence
    cd document-intelligence
    # Place main.py and requirements.txt here
    ```

2.  **Create `requirements.txt`:**
    Make sure you have a `requirements.txt` file in the same directory as `main.py` with the following content:

    ```
    PyPDF2==3.0.1
    sentence-transformers==2.7.0
    scikit-learn==1.5.0
    ```
    *(Note: You can check PyPI for the latest compatible versions if desired.)*

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    The `sentence-transformers` model (`all-MiniLM-L6-v2`) will be automatically downloaded the first time the script runs.

4.  **Prepare input directory:**
    Create a `pdfs` directory in the same location as `main.py` and place your PDF files inside it.

    ```bash
    mkdir pdfs
    # Copy your_document_1.pdf, your_document_2.pdf, etc., into the 'pdfs' directory
    ```

5.  **Run the application:**
    Open `main.py` and locate the `if __name__ == "__main__":` block.
    By default, it runs with the "PhD Researcher in Computational Biology" persona. You can change this to "Data Scientist" or add your own personas to the `personas_data` dictionary.

    ```python
    if __name__ == "__main__":
        # Example usage:
        run_document_intelligence_local(selected_persona_name="PhD Researcher in Computational Biology")
        # To run for Data Scientist:
        # run_document_intelligence_local(selected_persona_name="Data Scientist")
    ```

    Now, execute the script:

    ```bash
    python main.py
    ```

    The script will print progress logs to the console and save the resulting JSON file(s) to a newly created `output` directory in your project root.

---

### Running with Docker

Using Docker provides a consistent and isolated environment for the application, avoiding dependency conflicts.

1.  **Ensure you have the `main.py` and `requirements.txt` files** in your project's root directory.

2.  **Create the `Dockerfile`** in the same directory as `main.py`:

    ```dockerfile
    # Use a slim Python 3.9 image optimized for AMD64 architecture
    FROM --platform=linux/amd64 python:3.9-slim-buster

    # Set the working directory inside the container
    WORKDIR /app

    # Copy the requirements file into the container
    COPY requirements.txt .

    # Install Python dependencies from requirements.txt
    RUN pip install --no-cache-dir --upgrade pip && \
        pip install --no-cache-dir -r requirements.txt

    # Create directories that will be used for input/output inside the container
    # These paths (/app/pdfs and /app/output) must match the directories
    # expected by the Python script (PDF_DIR and OUTPUT_DIR)
    RUN mkdir -p /app/pdfs /app/output

    # Copy your application source code into the container
    COPY main.py .

    # Define the command to run your application when the container starts
    CMD ["python", "main.py"]
    ```

3.  **Build the Docker image:**
    Navigate to the directory containing your `Dockerfile`, `main.py`, and `requirements.txt`.

    ```bash
    docker build -t persona-doc-intelligence .
    ```

4.  **Prepare your input PDF files:**
    Place your PDF files in a directory on your host machine (e.g., `./my_pdfs`). This `my_pdfs` directory will be mounted to the container's `/app/pdfs`.

5.  **Run the Docker container:**
    You will need to mount your local input (`pdfs`) and output (`output`) directories to the container's respective directories.

    ```bash
    docker run \
      -v "$(pwd)/pdfs:/app/pdfs" \
      -v "$(pwd)/output:/app/output" \
      persona-doc-intelligence
    ```
    * `$(pwd)/pdfs`: This refers to your local `pdfs` directory containing your input PDFs.
    * `$(pwd)/output`: This is where the generated JSON output files will be saved on your local machine.

    The first time you run the container, the `all-MiniLM-L6-v2` model will be downloaded inside the container. Subsequent runs will use the cached model. After execution, check your local `output` directory for the extracted JSON reports.

---

## Output Format

The output will be a JSON file (e.g., `document_intelligence_output_YYYYMMDD_HHMMSS.json`) with the following structure:

```json
{
  "metadata": {
    "input_documents": [
      "document1.pdf",
      "document2.pdf"
    ],
    "persona": {
      "role": "PhD Researcher in Computational Biology",
      "expertise": [
        "Graph Neural Networks",
        "Drug Discovery",
        "Bioinformatics"
      ]
    },
    "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks",
    "processing_timestamp": "2024-07-28T10:30:00Z"
  },
  "extracted_sections": [
    {
      "document": "document1.pdf",
      "page_number": [5],
      "section_title": "Relevant Section from document1.pdf on Page 5",
      "importance_rank": 0.789
    },
    {
      "document": "document2.pdf",
      "page_number": [12],
      "section_title": "Relevant Section from document2.pdf on Page 12",
      "importance_rank": 0.654
    }
    // ... more highly relevant sections
  ],
  "subsection_analysis": [
    {
      "document": "document1.pdf",
      "page_number": 5,
      "refined_text": "This is the actual text chunk from document1.pdf that was identified as relevant."
    },
    {
      "document": "document2.pdf",
      "page_number": 12,
      "refined_text": "Another relevant text chunk from document2.pdf providing detailed information."
    }
    // ... all relevant text chunks
  ]
}
