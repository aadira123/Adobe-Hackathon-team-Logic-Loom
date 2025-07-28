# Persona-Driven Document Intelligence

## Connect What Matters — For the User Who Matters

This project implements an intelligent document analysis system designed to extract and prioritize the most relevant sections from a collection of PDF documents based on a specific user persona and their "job-to-be-done." It's built to be generic and adaptable to various domains, personas, and tasks.

## Challenge Brief

The core challenge is to build a system that acts as an intelligent document analyst. Given a collection of 3-10 related PDF documents, a persona definition (role, expertise, focus areas), and a concrete "job-to-be-done" for that persona, the system identifies and extracts the most relevant sections.

### Key Aspects:

* **Generic Solution:** The system is designed to generalize across diverse document types (research papers, financial reports, textbooks, news articles), personas (researcher, student, salesperson, journalist, entrepreneur), and jobs-to-be-done (literature review, financial analysis, exam preparation).
* **Input Specifications:**
    * **Document Collection:** 3-10 related PDF files.
    * **Persona Definition:** Role description with specific expertise and focus areas.
    * **Job-to-be-Done:** Concrete task the persona needs to accomplish.
* **Output Specifications:** A JSON file adhering to the `challenge1b_output.json` format, including:
    * **Metadata:** Input documents, persona details, job-to-be-done, processing timestamp.
    * **Extracted Sections:** Document, page number (list), section title, importance rank.
    * **Sub-section Analysis:** Document, page number, refined text.
* **Constraints:**
    * Must run on CPU only.
    * Model size $\le$ 1GB.
    * Processing time $\le$ 60 seconds for a document collection (3-5 documents).
    * No internet access allowed during execution.

## Sample Test Cases

To illustrate the system's versatility, consider these examples:

1.  **Academic Research:**
    * **Documents:** 4 research papers on "Graph Neural Networks for Drug Discovery."
    * **Persona:** PhD Researcher in Computational Biology.
    * **Job:** "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks."
2.  **Business Analysis:**
    * **Documents:** 3 annual reports from competing tech companies (2022-2024).
    * **Persona:** Investment Analyst.
    * **Job:** "Analyze revenue trends, R&D investments, and market positioning strategies."
3.  **Educational Content:**
    * **Documents:** 5 chapters from organic chemistry textbooks.
    * **Persona:** Undergraduate Chemistry Student.
    * **Job:** "Identify key concepts and mechanisms for exam preparation on reaction kinetics."

## Methodology (`approach_explanation.md`)

Our approach leverages a combination of text extraction, semantic understanding, and similarity-based ranking to achieve persona-driven document intelligence.

1.  **Text Extraction:** We utilize `PyPDF2` to robustly extract text content from the input PDF documents. This ensures we can process various PDF structures.
2.  **Text Chunking and Cleaning:** The extracted raw text is cleaned to remove extraneous whitespace and then segmented into manageable chunks. A basic chunking strategy with overlap is employed to maintain contextual integrity across chunk boundaries. Each chunk is associated with its originating filename and a simplified page number.
3.  **Semantic Embedding:** A pre-trained `SentenceTransformer` model (`all-MiniLM-L6-v2`) is used to convert both the persona's "job-to-be-done" and each document chunk into high-dimensional numerical vectors (embeddings). This model is chosen for its balance of performance and efficiency, adhering to the model size constraint.
4.  **Relevance Scoring (Cosine Similarity):** The core of the intelligence lies in calculating the cosine similarity between the "job-to-be-done" embedding and the embedding of each document chunk. Cosine similarity measures the angular difference between vectors, effectively quantifying their semantic relatedness.
5.  **Section Prioritization:** Chunks with a cosine similarity score above a predefined `THRESHOLD` (e.g., 0.5) are considered relevant. These relevant chunks form the "extracted sections" and are further refined for "sub-section analysis."
6.  **Output Generation:** The identified relevant sections are then compiled into a structured JSON output, including metadata about the input, persona, and job, along with the extracted content, its importance rank (based on similarity score), and original page numbers. The extracted sections are sorted by importance rank in descending order.

This modular design ensures that each component can be optimized independently, contributing to the overall efficiency and accuracy of the system while adhering to the specified resource and execution constraints. The pre-loading of the SentenceTransformer model and the CPU-only execution ensure compliance with the challenge requirements.

## Dockerfile

The `Dockerfile` used to build the container image for this project is as follows:

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
RUN mkdir -p /app/input /app/output

# Copy your application source code into the container
COPY src/ /app/src/

# Define the command to run your application when the container starts
CMD ["python", "src/main.py"]
```

## Setup and Execution

### Prerequisites

* Docker (recommended for easy setup and reproducibility)
* Python 3.9 (if running locally without Docker)

### 1. Using Docker (Recommended)

The easiest way to run this project is by using Docker.

**a. Prepare Input PDFs:**
Create a directory named `pdfs` in the same root directory as your `Dockerfile`. Place your input PDF documents (3-10 related PDFs) into this `pdfs` directory.

Example:
├── Dockerfile
├── requirements.txt
├── src/
│   └── main.py
└── pdfs/
├── document1.pdf
├── document2.pdf
└── ...

**b. Build Command**

Navigate to the root directory of your project (where `Dockerfile` and `requirements.txt` are located) and run:

```bash
docker build --platform linux/amd64 -t <document-intelligence-app> .
```
**c. Run Command**

To execute the system, ensure your input PDFs are in a pdfs folder at the root of your project and that an output folder exists or will be created for the results.

```Bash

docker run --rm \
    -v "$(pwd)/pdfs:/app/pdfs" \
    -v "$(pwd)/output:/app/output" \
    --network none \
    <reponame.someidentifier>
```
    on Windows: If you are using Command Prompt, replace $(pwd) with %cd%. If using Git Bash or WSL, $(pwd) should work.

Example for Windows Command Prompt:


```Bash

  docker run --rm ^
    -v "%cd%/pdfs:/app/pdfs" ^
    -v "%cd%/output:/app/output" ^
    --network none ^
    <document-intelligence-app>
```

    
 **Changing Persona:**
By default, the main.py script is set to run with "PhD Researcher in Computational Biology". To change the persona, you would typically modify src/main.py before building the Docker image or pass it as an argument if your script supported it. For this submission, please modify src/main.py as needed before building the image.

### 2. Running Locally (Without Docker)
a. Install Dependencies:
First, ensure you have Python 3.9 installed. Then, install the required libraries:
```

```Bash

pip install -r requirements.txt
```
Your requirements.txt should contain:
```Bash
PyPDF2
sentence-transformers
scikit-learn
```
b. Prepare Input PDFs:
Create a directory named pdfs in the root directory of your project (the same level as src/). Place your input PDF documents (3-10 related PDFs) into this pdfs directory.

Example Project Structure for Local Run:

```Bash
├── requirements.txt
├── src/
│   └── main.py
├── pdfs/
│   ├── document1.pdf
│   ├── document2.pdf
│   └── ...
└── output/  <-- This directory will be created if it doesn't exist
```
c. Run the Script:
Navigate to the src directory and run the main.py script:

```Bash

cd src
python main.py
```
The script will process the PDFs in the pdfs directory (one level up from src based on your PDF_DIR setting ../pdfs/) and save the output JSON to the output directory (also one level up, ../output/).

**Changing Persona:**
You can modify the selected_persona_name variable directly within src/main.py to test with different personas defined in the personas_data dictionary.

**Output Structure**
The output will be a JSON file named something like document_intelligence_output_YYYYMMDD_HHMMSS.json in the output/ directory, conforming to the following structure:

```bash

JSON

{
  "metadata": {
    "input_documents": [
      "document1.pdf",
      "document2.pdf"
      // ...
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
    "processing_timestamp": "2025-07-28T19:20:59Z"
  },
  "extracted_sections": [
    {
      "document": "document_a.pdf",
      "page_number": [5],
      "section_title": "Relevant Section from document_a.pdf on Page 5",
      "importance_rank": 0.85
    },
    {
      "document": "document_b.pdf",
      "page_number": [12],
      "section_title": "Relevant Section from document_b.pdf on Page 12",
      "importance_rank": 0.78
    }
    // ... more relevant sections, sorted by importance_rank
  ],
  "subsection_analysis": [
    {
      "document": "document_a.pdf",
      "page_number": 5,
      "refined_text": "Detailed methodology for graph neural network implementation..."
    },
    {
      "document": "document_b.pdf",
      "page_number": 12,
      "refined_text": "Performance benchmarks showing comparison with other models..."
    }
    // ... more detailed sub-sections
  ]
}
```
