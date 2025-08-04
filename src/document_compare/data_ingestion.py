import os
from pathlib import Path
import sys
import fitz
import uuid
from datetime import datetime
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentIngestion:
    def __init__(self, base_dir: str = "data\\document_compare"):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)


    def delete_existing_files(self):
        """
        Deletes existing files in the specified path
        """
        try:
            if self.base_dir.exists() and self.base_dir.is_dir():
                for file in self.base_dir.iterdir():
                    if file.is_file():
                        file.unlink()
                        self.log.info("File Deleted", path = str(file))
                self.log.info("Directory cleaned", directory = str(self.base_dir))

        except Exception as e:
            self.log.error(f"Error deleting existing files: {e}")
            raise DocumentPortalException("Error deleting existing files", sys)
        

    def save_uploaded_files(self, reference_file, actual_file):
        """
        Save uploaded files in a specific directory
        """
        try:
            self.delete_existing_files()
            self.log.info("Existing files deleted successfully")

            ref_path = self.base_dir/reference_file.name
            act_path = self.base_dir/actual_file.name

            if not reference_file.name.endswith(".pdf") or not actual_file.name.endswith(".pdf"):
                raise ValueError("Reference file must be a PDF")
            
            with open(ref_path, "wb") as f:
                f.write(reference_file.getbuffer())

            with open(act_path, "wb") as f:
                f.write(actual_file.getbuffer())

            self.log.info("Files saved", reference=str(ref_path), actual=str(act_path))
            return ref_path, act_path

        except Exception as e:
            self.log.error(f"Error saving uploaded files: {e}") 
            raise DocumentPortalException("Error saving uploaded files", sys)

    def read_pdf(self, pdf_path:str) -> str:
        """
        Read and extract PDF file text from each page
        """
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted: {pdf_path.name}")

                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()  # type: ignore
                    if text.strip():
                        all_text.append(f"\n --- Page {page_num + 1} --- \n{text}")

            self.log.info("PDF read successfully", file=str(pdf_path), pages=len(all_text))
            return "\n".join(all_text)

        except Exception as e:
            self.log.error(f"Error reading PDF file: {e}")
            raise DocumentPortalException("Error reading PDF file", sys)
        
    
    def combine_documents(self) -> str:
        """
        Combine content of all PDFs in session folder into a single string.
        """
        try:
            doc_parts = []
            for file in sorted(self.base_dir.iterdir()):
                if file.is_file() and file.suffix.lower() == ".pdf":
                    content = self.read_pdf(file)
                    doc_parts.append(f"Document: {file.name}\n{content}")

            combined_text = "\n\n".join(doc_parts)
            self.log.info("Documents combined", count=len(doc_parts))
            return combined_text

        except Exception as e:
            self.log.error("Error combining documents", error=str(e))
            raise DocumentPortalException("Error combining documents", sys)