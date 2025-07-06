import base64
import os
from pathlib import Path
import subprocess
from dotenv import load_dotenv

import fitz  # PyMuPDF
import openai

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_text_from_image(image_path: str) -> str:
    base64_image = encode_image(image_path)
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an expert in handwritten text extraction. Your task is to extract all text from the provided image, including handwritten and typed text.\nPlease be as precise as possible.\nProvide only the transcribed text, without any additional comments, introductions, or explanations. Be mostly accurate, with mathematical expressions, use latex expressions to transcribe them."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=2048,
    )
    return response.choices[0].message.content


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    temp_dir = Path("./app/temp_pdf_images")
    temp_dir.mkdir(parents=True, exist_ok=True)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        if len(set(pix.samples)) < 10:
            print(f"Skipping blank page {page_num + 1}")
            continue
        image_path = temp_dir / f"page_{page_num + 1}.png"
        pix.save(str(image_path))
        try:
            text += f"--- Page {page_num + 1} ---\n"
            text += extract_text_from_image(str(image_path))
            text += "\n\n"
        finally:
            os.remove(image_path)
    try:
        os.rmdir(temp_dir)
    except OSError as e:
        print(f"Error removing temporary directory {temp_dir}: {e}")
    return text


def get_latex_preamble() -> str:
    return r"""
\documentclass[a4paper, 11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\title{SPML Summer 2023}
\author{Generative AI}
\date{\today}
\begin{document}
\maketitle
"""


def get_latex_postamble() -> str:
    return r"""
\end{document}
"""


def format_text_to_latex(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": "You are a LaTeX expert. Your task is to convert the following text into a well-structured LaTeX document body. You should organize the text into sections, subsections, and paragraphs. Correct any spelling or grammatical errors. Ensure that all mathematical formulas are correctly formatted using LaTeX syntax. Use inline math for formulas in text (e.g., $...$), and display math for equations on their own lines (e.g., \\begin{equation} ... \\end{equation} or $$...$$). Do not lose any information. Do not include the document preamble (like \\documentclass) or \\begin{document} and \\end{document} commands. Only provide the body of the document content itself."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        max_tokens=4096,
    )
    return response.choices[0].message.content


def compile_latex_to_pdf(tex_path: Path):
    if not tex_path.exists():
        print(f"Error: LaTeX source file '{tex_path}' not found.")
        return
    run_dir = tex_path.parent
    for i in range(2):
        print(f"Running pdflatex compilation pass {i + 1}...")
        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_path.name],
                cwd=run_dir,
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
        except FileNotFoundError:
            print("Error: 'pdflatex' command not found. Is a LaTeX distribution (like TeX Live, MiKTeX) installed and in your PATH?")
            return
        except subprocess.CalledProcessError as e:
            print(f"Error compiling LaTeX file on pass {i+1}. Return code: {e.returncode}")
            log_file = tex_path.with_suffix('.log')
            if log_file.exists():
                print(f"--- LaTeX Log File ({log_file}) ---")
                with open(log_file, 'r') as f:
                    print(f.read())
            else:
                print("--- stdout ---")
                print(e.stdout)
                print("--- stderr ---")
                print(e.stderr)
            return
    pdf_path = tex_path.with_suffix('.pdf')
    if pdf_path.exists():
        print(f"Successfully compiled '{tex_path.name}' to '{pdf_path.name}'")
    else:
        print(f"Error: PDF file was not created after compilation.")


def process_pdf_to_latex_pdf(pdf_path: str) -> str:
    """
    Takes a path to a PDF, extracts text, generates a LaTeX file,
    compiles it to a PDF, and returns the path to the generated PDF.
    """
    pdf_path_obj = Path(pdf_path)
    # 1. Extract text
    print(f"Processing {pdf_path_obj.name}...")
    extracted_text = extract_text_from_pdf(pdf_path)

    # 2. Format to LaTeX
    print("Formatting text to LaTeX...")
    latex_body = format_text_to_latex(extracted_text)
    preamble = get_latex_preamble()
    postamble = get_latex_postamble()
    full_latex_doc = preamble + latex_body + postamble

    # 3. Save .tex file
    output_tex_path = pdf_path_obj.with_suffix('.tex')
    print(f"Saving LaTeX document to '{output_tex_path}'...")
    with open(output_tex_path, 'w', encoding='utf-8') as f:
        f.write(full_latex_doc)

    # 4. Compile to PDF
    compile_latex_to_pdf(output_tex_path)

    output_pdf_path = output_tex_path.with_suffix('.pdf')
    if output_pdf_path.exists():
        return str(output_pdf_path)
    else:
        return None 