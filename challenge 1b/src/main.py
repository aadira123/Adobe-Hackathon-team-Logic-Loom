# pip install PyPDF2
# pip install sentence-transformers
import os
import datetime
import json
from PyPDF2 import PdfReader # Assuming you're using PyPDF2 for PDF reading
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re # For cleaning text
# # --- Configuration ---
# # IMPORTANT: For local execution, place your PDF files in a 'pdfs' subfolder
# # relative to where you run this script.
# PDF_DIR = "../pdfs/"
# OUTPUT_DIR = "./output/" # Output JSON will be saved here
# # Create output directory if it doesn't exist
# os.makedirs(OUTPUT_DIR, exist_ok=True)
# os.makedirs(PDF_DIR, exist_ok=True) # Ensure pdfs dir also exists, in case user forgets
# --- Configuration ---
# IMPORTANT: For local execution, place your PDF files in a 'pdfs' subfolder
# relative to where you run this script.
# Changed to raw string to handle backslashes correctly

# --- Configuration ---
# IMPORTANT: For local execution, place your PDF files in a 'pdfs' subfolder
# relative to where you run this script.
PDF_DIR = "./pdfs/"  # Change this line from the absolute Windows path
OUTPUT_DIR = "./output/" # Change this line from the absolute Windows path

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True) # Ensure pdfs dir also exists, in case user forgets

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True) # Ensure pdfs dir also exists, in case user forgets
# Model configuration
MODEL_PATH = 'all-MiniLM-L6-v2' # This is the model identifier for SentenceTransformer
# Load the SentenceTransformer model once globally
print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loading SentenceTransformer model from: {MODEL_PATH}")
model = SentenceTransformer(MODEL_PATH)
print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Model loaded successfully.")
# Cosine similarity threshold for relevance (adjust as needed)
THRESHOLD = 0.5 # Consider temporarily lowering to 0.1 for debugging if no results appear
# Define personas (customize this as per your application's needs)
personas_data = {
    "Data Scientist": {
        "role": "Data Scientist",
        "expertise": ["Machine Learning", "Statistical Analysis", "Data Visualization"],
        "job_to_be_done": "Identify key statistical findings and machine learning model performance metrics.",
    },
    "PhD Researcher in Computational Biology": {
        "role": "PhD Researcher in Computational Biology",
        "expertise": ["Graph Neural Networks", "Drug Discovery", "Bioinformatics"],
        "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks",
    },}
    # Add more personas as needed
# --- Helper Functions (You likely have these or similar) ---

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None
    return text

def clean_and_chunk_text(text, filename, max_chunk_size=512, overlap=50):
    """
    Cleans text, splits it into manageable chunks, and retains context.
    Adds filename and page_num (if available and relevant) to each chunk.
    """
    if text is None:
        return []

    # Simple cleaning: remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Split into chunks (you might have more sophisticated chunking logic)
    # This is a very basic chunking strategy
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    page_num = 1 # Basic page tracking (might need enhancement if your PDF parser gives page info)

    for word in words:
        if current_length + len(word) + 1 > max_chunk_size and current_chunk:
            chunks.append({
                "filename": filename,
                "page_num": page_num, # Simplified: assume each chunk starts on the same page for now
                "text_chunk": " ".join(current_chunk)
            })
            # For overlap, take the last 'overlap' words
            current_chunk = current_chunk[-overlap:]
            current_length = sum(len(w) for w in current_chunk) + len(current_chunk) - 1 if current_chunk else 0
        current_chunk.append(word)
        current_length += len(word) + 1 # +1 for space

    if current_chunk: # Add last chunk
        chunks.append({
            "filename": filename,
            "page_num": page_num, # Simplified
            "text_chunk": " ".join(current_chunk)
        })
    return chunks
# --- Main Document Intelligence Function ---

def run_document_intelligence_local(selected_persona_name):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Document Intelligence Process...")

    persona_info = personas_data.get(selected_persona_name)
    if not persona_info:
        print(f"Error: Persona '{selected_persona_name}' not found.")
        return {"error": f"Persona '{selected_persona_name}' not found."}

    persona_role = persona_info["role"]
    persona_expertise = persona_info["expertise"]
    job_to_be_done = persona_info["job_to_be_done"]

    # --- Step 1: Load Persona Embedding ---
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Encoding persona job-to-be-done...")
    persona_embedding = model.encode(job_to_be_done)
    persona_embedding_reshaped = persona_embedding.reshape(1, -1) # Reshape for cosine_similarity

    # --- Step 2: Discover and Process PDF Files ---
    all_pdf_filenames = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    if not all_pdf_filenames:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No PDF files found in {PDF_DIR}.")
        return {"error": "No PDF files found."}

    # Initialize lists to accumulate results from ALL documents
    # These will be flat lists as per your desired output structure
    all_extracted_sections = []
    all_sub_section_analysis = []
    input_documents_for_output = [] # To store names of files actually processed

    # --- Process each PDF document individually ---
    for pdf_filename in all_pdf_filenames:
        full_pdf_path = os.path.join(PDF_DIR, pdf_filename)
        input_documents_for_output.append(pdf_filename) # Add to list for metadata

        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing PDF: {pdf_filename}")

        # Extract text
        text_content = extract_text_from_pdf(full_pdf_path)
        if text_content is None:
            continue # Skip to next PDF if extraction failed

        # Chunk text (pass filename to chunker to include in chunk metadata)
        document_chunks = clean_and_chunk_text(text_content, pdf_filename)
        if not document_chunks:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No processable chunks found in {pdf_filename}. Skipping.")
            continue

        # Embed chunks
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Embedding {len(document_chunks)} chunks from {pdf_filename}...")
        chunk_texts = [chunk['text_chunk'] for chunk in document_chunks]
        chunk_embeddings = model.encode(chunk_texts, show_progress_bar=False)

        # --- Step 3: Calculate Similarities for chunks from this PDF ---
        # Note: We iterate through chunks, calculate similarity, and append to the *global* lists.
        for i, doc_item in enumerate(document_chunks):
            current_chunk_embedding = chunk_embeddings[i].reshape(1, -1)
            similarity = cosine_similarity(persona_embedding_reshaped, current_chunk_embedding)[0][0]

            if similarity >= THRESHOLD:
                # Add to main extracted sections list
                all_extracted_sections.append({
                    "document": doc_item["filename"],
                    # Note: page_number as a list requires more sophisticated chunking
                    # For now, if a chunk is mainly from one page, keep it as single or make a list like [doc_item["page_num"]]
                    "page_number": [doc_item["page_num"]], # Example: force to list for consistency with your desired output
                    "section_title": f"Relevant Section from {doc_item['filename']} on Page {doc_item['page_num']}",
                    "importance_rank": float(similarity) # Ensure it's a float
                })

                # Add to main sub-section analysis list
                all_sub_section_analysis.append({
                    "document": doc_item["filename"],
                    "page_number": doc_item["page_num"],
                    "refined_text": doc_item["text_chunk"]
                })
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Finished processing {pdf_filename}.")

    # --- Step 4: Finalize and Sort Extracted Sections (after all PDFs are processed) ---
    all_extracted_sections.sort(key=lambda x: x["importance_rank"], reverse=True)

    # --- Step 5: Prepare and Save JSON Output ---
    output_data = {
        "metadata": {
            "input_documents": input_documents_for_output, # List of all PDFs found and processed
            "persona": {
                "role": persona_role,
                "expertise": persona_expertise
            },
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.datetime.now().isoformat(timespec='seconds') + 'Z' # ISO 8601 with Z for UTC
        },
        "extracted_sections": all_extracted_sections,
        "subsection_analysis": all_sub_section_analysis
    }

    # Save to JSON file
    timestamp_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = os.path.join(OUTPUT_DIR, f"document_intelligence_output_{timestamp_str}.json")

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Document intelligence process completed. Output saved to {output_filename}")
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error saving output to JSON: {e}")

    return output_data
# --- Main execution block (when the script is run directly) ---
if __name__ == "__main__":
    # Example usage:
    # You can change the selected_persona_name here
    run_document_intelligence_local(selected_persona_name="PhD Researcher in Computational Biology")
    # run_document_intelligence_local(selected_persona_name="Data Scientist")




