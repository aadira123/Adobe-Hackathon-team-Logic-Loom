

### app.py (Single File Code)


import os
import json
import logging
import fitz  # PyMuPDF

# --- Configuration and Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define input and output directories relative to where the script is run
INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# --- PDF Outline Extractor Class ---
class PDFOutlineExtractor:
    def __init__(self):
        self.heading_style_rules = [] # Will store (font_name, font_size, is_bold, level) tuples
        self.body_text_max_size = 12.0 # Upper bound for typical body text. Tune this!

    def _analyze_fonts_and_set_heuristics(self, doc):
        """
        Analyzes font sizes and styles across the document to infer potential heading levels.
        This is a heuristic-based approach. For robust results across diverse PDFs,
        this method often requires significant tuning or more advanced techniques
        (e.g., text clustering, machine learning).
        """
        unique_text_styles = {} # (font_name, font_size, is_bold) -> total_text_length

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            try:
                blocks = page.get_text("dict")["blocks"]
                for b in blocks:
                    if b['type'] == 0: # text block
                        for line in b['lines']:
                            for span in line['spans']:
                                font_name = span['font']
                                font_size = round(span['size'], 1)
                                # Basic check for bold in font name, common for bold fonts
                                is_bold = "bold" in font_name.lower() or "bolder" in font_name.lower() or "heavy" in font_name.lower()

                                style_key = (font_name, font_size, is_bold)
                                unique_text_styles[style_key] = unique_text_styles.get(style_key, 0) + len(span['text']) # Sum of text length

            except Exception as e:
                logging.warning(f"Could not extract text dict from page {page_num + 1}: {e}")
                continue

        # Sort styles by size and then by total text length (prominence)
        sorted_styles = sorted(unique_text_styles.items(),
                               key=lambda item: (item[0][1], item[1]), # Sort by font size, then by text length
                               reverse=True)

        logging.info(f"Analyzed unique text styles: {sorted_styles}")

        heading_candidates = []
        seen_sizes = set()

        # Find distinct font sizes that are candidates for headings
        for (font_name, font_size, is_bold), total_len in sorted_styles:
            if font_size < 8.0: # Filter out very small text (likely non-content)
                continue
            if font_size not in seen_sizes:
                heading_candidates.append((font_name, font_size, is_bold, total_len))
                seen_sizes.add(font_size)

        self.heading_style_rules = []
        if heading_candidates:
            # Filter candidates to only those significantly larger than the assumed body text max size
            content_heading_candidates = [
                (fn, fs, ib, tl) for fn, fs, ib, tl in heading_candidates
                if fs > self.body_text_max_size
            ]
            content_heading_candidates.sort(key=lambda x: x[1], reverse=True) # Sort again by size

            # Assign H1, H2, H3 based on distinct prominent sizes
            if content_heading_candidates:
                # The largest candidate is H1
                self.heading_style_rules.append(
                    (content_heading_candidates[0][0], content_heading_candidates[0][1], content_heading_candidates[0][2], "H1")
                )
                if len(content_heading_candidates) > 1:
                    # Second candidate is H2, if significantly smaller than H1
                    if content_heading_candidates[1][1] < content_heading_candidates[0][1] * 0.9: # 10% smaller to be distinct
                        self.heading_style_rules.append(
                            (content_heading_candidates[1][0], content_heading_candidates[1][1], content_heading_candidates[1][2], "H2")
                        )
                    if len(content_heading_candidates) > 2:
                        # Third candidate is H3, if significantly smaller than H2
                        if content_heading_candidates[2][1] < content_heading_candidates[1][1] * 0.9:
                            self.heading_style_rules.append(
                                (content_heading_candidates[2][0], content_heading_candidates[2][1], content_heading_candidates[2][2], "H3")
                            )

        logging.info(f"Inferred heading style rules: {self.heading_style_rules}")


    def extract_outline(self, pdf_path):
        doc = fitz.open(pdf_path)
        
        self._analyze_fonts_and_set_heuristics(doc)

        outline = []
        title = ""

        last_span_end_y = 0 # To track vertical spacing between text elements
        last_page_num = -1

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            
            # Reset Y tracking for a new page
            if page_num != last_page_num:
                last_span_end_y = 0
                last_page_num = page_num

            blocks = page.get_text("dict")["blocks"]

            for b_idx, b in enumerate(blocks):
                if b['type'] == 0: # text block
                    for l_idx, line in enumerate(b['lines']):
                        for s_idx, span in enumerate(line['spans']):
                            text = span['text'].strip()
                            if not text:
                                continue

                            font_name = span['font']
                            font_size = round(span['size'], 1)
                            is_bold = "bold" in font_name.lower() or "bolder" in font_name.lower() or "heavy" in font_name.lower()

                            span_start_y = span['bbox'][1]

                            # Title detection: Try to find the most prominent text on the first page
                            if page_num == 0 and not title and font_size > self.body_text_max_size:
                                # Simple heuristic: first large text block on the first page
                                # A better heuristic might check if it's visually centered or has unique high prominence.
                                if b_idx == 0 and l_idx == 0 and s_idx == 0: # Very first text element
                                     title = text
                                     logging.info(f"Detected potential title: '{title}' on page {page_num + 1}")
                                     last_span_end_y = span['bbox'][3]
                                     continue # Skip further heading detection for the title

                            # Heading detection using inferred rules
                            current_level = None
                            for rule_font_name, rule_font_size, rule_is_bold, level_name in self.heading_style_rules:
                                if (font_size == rule_font_size and
                                    (not rule_is_bold or is_bold)): # If rule requires bold, span must be bold
                                    current_level = level_name
                                    break

                            if current_level:
                                # Contextual check: Ensure it's a distinct heading, not part of flowing text.
                                # Check for a significant vertical gap above the text, or if it's the first text on page/block.
                                vertical_gap = span_start_y - last_span_end_y
                                
                                # Threshold for a "significant gap" (e.g., 1.5 times the max body text height)
                                if vertical_gap > self.body_text_max_size * 1.5 or last_span_end_y == 0:
                                    
                                    # Avoid adding duplicate headings (e.g., if extracted multiple times due to slight layout variations)
                                    is_duplicate = False
                                    if outline:
                                        last_item = outline[-1]
                                        # Same text, same level, and on the same page (or very close lines on same page)
                                        if (last_item["text"] == text and
                                            last_item["level"] == current_level and
                                            last_item["page"] == page_num + 1):
                                            is_duplicate = True

                                    if not is_duplicate:
                                        outline.append({
                                            "level": current_level,
                                            "text": text,
                                            "page": page_num + 1
                                        })
                                        logging.info(f"Detected {current_level}: '{text}' on page {page_num + 1}")
                                        
                                    last_span_end_y = span['bbox'][3] # Update last Y
                                    break # Move to next line after finding a heading for this line

                            last_span_end_y = span['bbox'][3] # Always update last Y position

        doc.close()
        
        # Post-processing: If title is still empty, try to derive from first H1
        if not title and outline:
            first_h1_on_page_1 = next((item for item in outline if item["level"] == "H1" and item["page"] == 1), None)
            if first_h1_on_page_1:
                title = first_h1_on_page_1["text"]
                # Remove this H1 from the outline if it's now considered the title
                outline = [item for item in outline if not (item["level"] == "H1" and item["text"] == title and item["page"] == 1)]
                logging.info(f"Promoted first H1 on page 1 to title: '{title}'")
            elif outline: # As a last resort, use the first general heading found
                title = outline[0]["text"]
                logging.info(f"Using first detected outline item as title: '{title}'")


        return {"title": title, "outline": outline}

# --- Main Execution Logic ---
def main():
    if not os.path.exists(INPUT_DIR):
        logging.error(f"Input directory not found: {INPUT_DIR}. Please create it and place PDFs inside.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logging.info(f"Created output directory: {OUTPUT_DIR}")

    extractor = PDFOutlineExtractor()

    pdf_found = False
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_found = True
            pdf_path = os.path.join(INPUT_DIR, filename)
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            logging.info(f"Processing {pdf_path}...")
            try:
                result = extractor.extract_outline(pdf_path)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                logging.info(f"Successfully processed {filename}. Output saved to {output_path}")
            except Exception as e:
                logging.error(f"Error processing {filename}: {e}", exc_info=True) # exc_info to print traceback

    if not pdf_found:
        logging.warning(f"No PDF files found in the input directory: {INPUT_DIR}")


if __name__ == "__main__":
    main()

