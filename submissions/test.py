import PyPDF2
from profanity_check import predict, predict_prob

# Predefined list of sexual content words
sexual_content_keywords = [
    'sex', 'sexual', 'nude', 'porn', 'erotic', 'intimate', 'explicit', 'naked',
    'orgasm', 'penetration', 'masturbate', 'climax', 'fetish', 'seduce', 'lust'
]

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def detect_profanity(text):
    """Detects profanity in text."""
    lines = text.splitlines()
    profane_lines = []
    for line in lines:
        if predict([line])[0] == 1:
            profane_lines.append(line)
        if len(profane_lines) >= 5:  # Get only first 5 occurrences
            break
    return profane_lines

def detect_sexual_content(text):
    """Detects sexual content based on keyword matches."""
    lines = text.splitlines()
    sexual_lines = []
    for line in lines:
        for word in sexual_content_keywords:
            if word.lower() in line.lower():
                sexual_lines.append(line)
                break
        if len(sexual_lines) >= 5:  # Get only first 5 occurrences
            break
    return sexual_lines

def scan_pdf_for_content(pdf_path):
    """Scans a PDF for profanity and sexual content and prints the first 5 occurrences."""
    # Step 1: Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Step 2: Detect profanity
    print("Scanning for Profanity...")
    profane_content = detect_profanity(text)
    
    # Step 3: Detect sexual content
    print("\nScanning for Sexual Content...")
    sexual_content = detect_sexual_content(text)

    # Step 4: Output the results
    print("\nProfane Content (First 5 Occurrences):")
    for idx, line in enumerate(profane_content, 1):
        print(f"{idx}. {line}")

    print("\nSexual Content (First 5 Occurrences):")
    for idx, line in enumerate(sexual_content, 1):
        print(f"{idx}. {line}")

# Example usage
pdf_path = 'sample.pdf'  # Replace with the actual PDF file path
scan_pdf_for_content(pdf_path)
