
# PDF Outline Extractor

This project provides a Python-based tool to extract the hierarchical outline (table of contents) from PDF documents. It analyzes font styles and sizes within the PDF to infer headings and their levels (H1, H2, H3), then outputs this structure as a JSON file.

---

## Features

* **Automated Outline Extraction**: Automatically scans PDF content to identify potential headings.
* **Heuristic-Based Analysis**: Uses font size, boldness, and vertical spacing to determine heading hierarchy.
* **JSON Output**: Generates a structured JSON file containing the detected title and outline with text, level, and page number.
* **Batch Processing**: Processes all PDF files found in a designated input directory.
* **Dockerized**: Easily deployable using Docker for consistent environments.

---

## How it Works

The `PDFOutlineExtractor` class first performs a heuristic analysis of the PDF to identify dominant font styles and sizes that are likely used for headings. It then iterates through each page, identifying text spans that match these inferred heading styles. It also attempts to identify a main title for the document.

The outline is constructed as a list of dictionaries, each containing:
* `level`: The inferred heading level (e.g., "H1", "H2", "H3").
* `text`: The content of the heading.
* `page`: The page number where the heading was found.

---

## Getting Started

### Prerequisites

* Python 3.8+
* pip (Python package installer)
* Docker (if you plan to use the Dockerized version)

### Local Setup and Execution

1.  **Clone the repository (or save the files):**
    If you have this as part of a larger project, ensure `app.py` is in your project root. If it's a standalone script, create a directory for it.

    ```bash
    mkdir pdf-outline-extractor
    cd pdf-outline-extractor
    # Place app.py and requirements.txt here
    ```

2.  **Create `requirements.txt`:**
    Make sure you have a `requirements.txt` file in the same directory as `app.py` with the following content:

    ```
    PyMuPDF==1.23.9 # You can use a newer version if available
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepare input directory:**
    Create an `input` directory in the same location as `app.py` and place your PDF files inside it.

    ```bash
    mkdir input
    # Copy your_document.pdf into the 'input' directory
    ```

5.  **Run the application:**

    ```bash
    python app.py
    ```

    The script will process all PDFs in the `input` directory and save the resulting JSON files to a newly created `output` directory.

---

### Running with Docker

Using Docker provides a self-contained environment for the application.

1.  **Ensure you have the `app.py` and `requirements.txt` files** in your project root.

2.  **Create the `Dockerfile`** in the same directory as `app.py`:

    ```dockerfile
    # Use a slim Python image for smaller size and AMD64 compatibility
    FROM --platform=linux/amd64 python:3.9-slim-buster

    # Set the working directory in the container
    WORKDIR /app

    # Copy the requirements file into the container
    COPY requirements.txt .

    # Install Python dependencies
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the main script into the container
    COPY app.py .

    # Create input and output directories as expected by the application
    RUN mkdir -p /app/input /app/output

    # Command to run the application when the container starts
    CMD ["python", "app.py"]
    ```

3.  **Build the Docker image:**
    Navigate to the directory containing your `Dockerfile`, `app.py`, and `requirements.txt`.

    ```bash
    docker build -t pdf-outline-extractor .
    ```

4.  **Prepare your input PDF files:**
    Place your PDF files in a directory on your host machine (e.g., `./my_pdfs_to_process`).

5.  **Run the Docker container:**
    You will need to mount your local input and output directories to the container's `/app/input` and `/app/output` directories, respectively.

    ```bash
    docker run -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" pdf-outline-extractor
    ```
    * `$(pwd)/input`: This refers to your local `input` directory containing your PDFs.
    * `$(pwd)/output`: This is where the generated JSON files will be saved on your local machine.

    After running, check your local `output` directory for the extracted JSON outlines.

---

## Output Format

The output for each PDF will be a JSON file named after the original PDF (e.g., `document.json` for `document.pdf`), with the following structure:

```json
{
  "title": "Detected Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Main Section Title",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Subsection Heading",
      "page": 3
    },
    {
      "level": "H3",
      "text": "Sub-subsection Detail",
      "page": 5
    }
    // ... more outline items
  ]
}