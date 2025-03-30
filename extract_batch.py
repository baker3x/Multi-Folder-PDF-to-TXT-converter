# extract_recursive.py
import os
import glob # Used for finding files matching a pattern
from PyPDF2 import PdfReader
import sys

# --- Configuration ---
# Set the path to the TOP-LEVEL FOLDER containing your PDF files and subfolders
pdf_base_folder_path = '/Users/baker3x/UnpluggedAI/gemma/pdfs' # <--- CHANGE THIS (The folder holding the subfolders)

# Set the path to the FOLDER where you want the mirrored output structure saved
output_base_folder_path = '/Users/baker3x/UnpluggedAI/gemma/pdfs_done' # <--- CHANGE THIS
# --- End Configuration ---

def extract_text_from_pdf(pdf_path):
    """Extracts text from all pages of a PDF file."""
    # Using relative path for cleaner logging in recursive mode
    try:
        relative_path = os.path.relpath(pdf_path, pdf_base_folder_path)
    except ValueError: # Happens if paths are on different drives on Windows
        relative_path = os.path.basename(pdf_path) # Fallback to basename
    print(f"--- Processing PDF: {relative_path} ---")

    try:
        reader = PdfReader(pdf_path)
        # Optional: Check if the PDF is encrypted
        if reader.is_encrypted:
            try:
                reader.decrypt('')
            except Exception as e:
                print(f"Error: Could not decrypt {relative_path}. Skipping. Error: {e}")
                return None

        full_text = ""
        num_pages = len(reader.pages)
        #print(f"Found {num_pages} pages.") # Reducing verbosity slightly for many files

        for page_num in range(num_pages):
            try:
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n\n" # Add text from the page
            except Exception as page_error:
                print(f"Error extracting text from page {page_num + 1} in {relative_path}: {page_error}")

        if not full_text:
             print(f"Warning: No text extracted from {relative_path}. It might be image-based.")

        return full_text

    except Exception as e:
        print(f"An error occurred while processing {relative_path}: {e}")
        return None

def save_text_to_file(text, output_path):
    """Saves the extracted text to a file, ensuring the directory exists."""
    if text is None:
        # Get relative path for logging
        try:
            relative_output_path = os.path.relpath(output_path, output_base_folder_path)
        except ValueError:
            relative_output_path = os.path.basename(output_path)
        print(f"No text extracted for the file corresponding to {relative_output_path}, nothing to save.")
        return False

    try:
        # Ensure the output directory exists *** This is the crucial part for mirroring ***
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            # Create all necessary parent directories
            os.makedirs(output_dir)
            #print(f"Created output directory: {output_dir}") # Less verbose

        # Write the text to the file using UTF-8 encoding
        with open(output_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(text)
        # Get relative path for logging
        try:
            relative_output_path = os.path.relpath(output_path, output_base_folder_path)
        except ValueError:
            relative_output_path = os.path.basename(output_path)
        print(f"Successfully saved text to: {relative_output_path}")
        return True
    except IOError as e:
        print(f"Error writing text to file {os.path.basename(output_path)}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during saving {os.path.basename(output_path)}: {e}")
        return False

# --- Main execution ---
if __name__ == "__main__":
    # 1. Check if input base folder exists
    if not os.path.isdir(pdf_base_folder_path):
        print(f"Error: Input base folder not found at {pdf_base_folder_path}")
        sys.exit(1)

    # 2. Output base folder creation is handled by save_text_to_file implicitly if needed,
    #    but we can check the base path is writable or create it upfront if preferred.
    #    Let's ensure the top-level output dir exists for clarity.
    try:
        os.makedirs(output_base_folder_path, exist_ok=True)
        print(f"Output will be saved within: {output_base_folder_path}")
    except OSError as e:
         print(f"Error: Could not create base output directory {output_base_folder_path}: {e}")
         sys.exit(1)

    # 3. Find all PDF files RECURSIVELY in the input folder (case-insensitive)
    # The '**' wildcard combined with recursive=True searches all subdirectories
    search_pattern_lower = os.path.join(pdf_base_folder_path, '**', '*.pdf')
    search_pattern_upper = os.path.join(pdf_base_folder_path, '**', '*.PDF')

    pdf_files = glob.glob(search_pattern_lower, recursive=True) + glob.glob(search_pattern_upper, recursive=True)
    pdf_files = list(set(pdf_files)) # Remove duplicates

    if not pdf_files:
        print(f"No PDF files found recursively in {pdf_base_folder_path}")
        sys.exit(0)

    print(f"Found {len(pdf_files)} PDF file(s) recursively.")
    print("-" * 20)

    # 4. Process each PDF file
    processed_count = 0
    failed_count = 0
    for i, pdf_path in enumerate(pdf_files):
        # Calculate relative path to maintain structure
        try:
            relative_path = os.path.relpath(pdf_path, pdf_base_folder_path)
        except ValueError as e:
             print(f"Warning: Could not determine relative path for {pdf_path} relative to {pdf_base_folder_path}. Skipping file. Error: {e}")
             failed_count += 1
             continue # Skip this file if relative path fails (e.g. different drives)

        # Generate the corresponding output file path maintaining the structure
        # Change the extension from .pdf/.PDF to .txt
        relative_path_no_ext = os.path.splitext(relative_path)[0]
        output_filename = relative_path_no_ext + '.txt'
        output_path = os.path.join(output_base_folder_path, output_filename)

        # Print progress (using relative path)
        print(f"Processing file {i + 1} of {len(pdf_files)}: [{relative_path}]")

        # Extract text
        extracted_text = extract_text_from_pdf(pdf_path) # Pass the full path here

        # Save text if extraction was successful
        if extracted_text is not None:
             # save_text_to_file will create subdirectories in output_path if they don't exist
             if save_text_to_file(extracted_text, output_path):
                 processed_count += 1
             else:
                 failed_count += 1
        else:
            failed_count += 1
        print("-" * 10) # Separator between files

    # 5. Print summary
    print("\n" + "=" * 20)
    print("Recursive Batch Processing Summary:")
    print(f"Total PDF files found: {len(pdf_files)}")
    print(f"Successfully processed and saved: {processed_count}")
    print(f"Failed or skipped: {failed_count}")
    print(f"Output saved in: {output_base_folder_path}")
    print("=" * 20)