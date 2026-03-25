import fitz  # PyMuPDF
from pathlib import Path


def pdf_to_md(pdf_path, md_path):
    doc = fitz.open(pdf_path)
    md = []

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        md.append(f"# Page {page_num + 1}\n{text}\n")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def convert_folder(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output folder if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all PDFs recursively
    pdf_files = input_path.rglob("*.pdf")

    for pdf_file in pdf_files:
        # Preserve relative structure (optional)
        relative_path = pdf_file.relative_to(input_path)
        md_file = (output_path / relative_path).with_suffix(".md")

        # Create subfolders if needed
        md_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"Converting: {pdf_file} → {md_file}")
        pdf_to_md(pdf_file, md_file)


if __name__ == "__main__":
    input_folder = "/Users/agolubin/git-repos/agolubinskiy4work/internal-rag-assistant/data/raw"
    output_folder = "/Users/agolubin/git-repos/agolubinskiy4work/internal-rag-assistant/data/raw/converted_md"

    convert_folder(input_folder, output_folder)