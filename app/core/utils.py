from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
import os, re
from collections import defaultdict
from app.core.config import settings
from app.models.schemas import Continuity
from google import genai
from google.genai import types
from pydantic import ValidationError
import json
from loguru import logger

client = genai.Client(api_key=settings.gemini_api_key)

def clean_filename(text, max_words=5):
    text = re.sub(r'[^\w\s]', '', text.replace('\n', ' '))
    words = text.strip().split()[:max_words]
    return "_".join(words) if words else "document"

def detect_continuity(page1_num_1_indexed,preceding_page_content,page2_num_1_indexed,following_page_content):
    model = "gemini-2.5-flash"
    prompt_text = f"""
    You are an expert document analysis AI. Your task is to determine if two provided text segments logically belong to consecutive pages of the same PDF document.

    Analyze the 'Preceding Page Content' and 'Following Page Content' below. Look for signs of continuity, consistent formatting (like headers, footers, or consistent paragraph breaks), shared topics, and logical flow of information. Pay attention to how sentences or paragraphs might transition between pages.

    ---
    Preceding Page Content (Page {page1_num_1_indexed}):
    ```
    {preceding_page_content}
    ```
    ---

    ---
    Following Page Content (Page {page2_num_1_indexed}):
    ```
    {following_page_content}
    ```
    ---

    Based on your analysis, do these two text segments appear to come from consecutive pages of the same PDF document?

    Output your answer **ONLY** as a JSON object with a single key "continuity" and a value of either "Yes" or "No".
    Example Output:
    ```json
    {{"continuity": "Yes"}}
    ```
    """
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt_text)
            ],
        ),
    ]
    # tools = [
    #     types.Tool(googleSearch=types.GoogleSearch(
    #     )),
    # ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        # tools=tools,
        response_mime_type="application/json",
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    try:
        # Extract JSON from response.text (removing code block markdown if any)
        raw_text = response.text.strip().strip("```json").strip("```")
        result = Continuity.model_validate_json(raw_text)
        return result
    except (ValidationError, json.JSONDecodeError) as e:
        print("Failed to parse response:", e)
        print("Raw response:", response.text)
        return None

def split_pdf(path, output_dir):
    pdf_dict = defaultdict(list)
    pdf_num = 1
    pdf_dict[pdf_num].append(0)
    logger.info("Starting the pdf split")
    with pdfplumber.open(path) as pdf:
        for i in range(len(pdf.pages) - 1):
            logger.info(f"processing page {i} and {i+1}")
            p1 = pdf.pages[i].extract_text_simple()
            p2 = pdf.pages[i+1].extract_text_simple()
            response = detect_continuity(i, p1, i+1, p2)
            if response.continuity.lower() == "yes":
                pdf_dict[pdf_num].append(i+1)
            else:
                pdf_num += 1
                pdf_dict[pdf_num].append(i+1)

    reader = PdfReader(path)
    os.makedirs(output_dir, exist_ok=True)
    result_files = []
    for doc_num, pages in pdf_dict.items():
        writer = PdfWriter()
        for p in pages:
            writer.add_page(reader.pages[p])
        filename = f"{clean_filename(reader.pages[pages[0]].extract_text())}_{doc_num}.pdf"
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "wb") as f:
            writer.write(f)
        result_files.append(output_path)
    return result_files