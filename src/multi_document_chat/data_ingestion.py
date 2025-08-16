
import uuid
from pathlib import Path
import sys
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import  DocumentPortalException
from utils.model_loader import ModelLoader
from datetime import datetime, timezone


class DocumentIngestor:

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

    def __init__(self, temp_dir :str = "data\\multi_document_chat", faiss_dir : str = "faiss_index", session_id:str | None = None):
        try:
            self.log = CustomLogger().get_logger(__name__)

            # base dirs
            self.temp_dir = Path(temp_dir)
            self.faiss_dir = Path(faiss_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            # sessionized paths
            self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
            self.session_temp_dir = self.temp_dir / self.session_id
            self.session_faiss_dir = self.faiss_dir / self.session_id
            self.session_temp_dir.mkdir(parents=True, exist_ok=True)
            self.session_faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader()
            self.log.info("DocumentIngestor initialized successfully", 
                           session_id = self.session_id,
                           temp_base = str(self.temp_dir), 
                           faiss_base = str(self.faiss_dir),
                           temp_path = str(self.session_temp_dir),
                           faiss_path = str(self.session_faiss_dir)
                           )

        except Exception as e:
            self.log.error("Failed to initialize class DocumentIngestor:", error = str(e))
            raise DocumentPortalException("Failed to initialize class DocumentIngestor:", sys)

    def ingest_files(self, uploaded_files):
        try:
            documents = []
            for uploaded_file in uploaded_files:
                ext = Path(uploaded_file.name).suffix.lower()
                if ext not in self.SUPPORTED_EXTENSIONS:
                    self.log.warning("Unsupported file type", file_name = uploaded_file.name)
                    continue
                unique_filename = f"{uuid.uuid4().hex[:8]}{ext}"
                temp_path = self.session_temp_dir / unique_filename

                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())

                self.log.info("File saved for ingestions", file_name = uploaded_file.name, saved_as = str(temp_path), session_id = self.session_id)

                if ext == ".pdf":
                    loader = PyPDFLoader(str(temp_path))
                elif ext == ".docx":
                    loader = Docx2txtLoader(str(temp_path))
                elif ext == ".txt":
                    loader = TextLoader(str(temp_path), encoding = "utf-8")
                else:
                    self.log.warning("Unsupported file type", file_name = uploaded_file.name)
                    continue

                docs = loader.load()
                documents.extend(docs)

            if not documents:
                raise DocumentPortalException("No valid documents loadded", sys)
            
            self.log.info("Documents loaded successfully", num_documents = len(documents), session_id = self.session_id)
            return self._create_retriever(documents)


        except Exception as e:
            self.log.error("Failed to ingest files", error = str(e))
            raise DocumentPortalException("Failed to ingest files", sys)
        

    def _create_retriever(self, documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 300)
            chunks = splitter.split_documents(documents)
            self.log.info("Documents split into chunks", num_chunks = len(chunks), session_id = self.session_id)

            embeddings = self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(chunks, embeddings)

            # Save FAISS index under session folder
            vectorstore.save_local(str(self.session_faiss_dir))
            self.log.info("FAISS index created and saved", session_id = self.session_id, faiss_path = str(self.session_faiss_dir))

            retriever = vectorstore.as_retriever(search_type = "similarty", search_kwargs = {"k": 5})

            self.log.info("FAISS retriever created and ready to use", session_id=self.session_id)
            return retriever

        except Exception as e:
            self.log.error("Failed to create retriever", error = str(e))    
            raise DocumentPortalException("Failed to create retriever", sys)

