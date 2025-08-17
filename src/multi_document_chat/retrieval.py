import sys
import os
from typing import List, Optional
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage

from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType


class ConversationalRAG:
    def __init__(self, session_id:str, retriever = None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.retriever = retriever

            self.llm = self._load_llm()
            self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            self.retriever = retriever

            self._build_lcel_chain()
            self.log.info("ConversationalRAG initialized", session_id=self.session_id)

        except Exception as e:
            self.log.error("Failed to initialize ConversationalRAG", error = str(e), session_id=self.session_id)
            raise DocumentPortalException("Failed to initialize ConversationalRAG", sys)
        

    def load_retreiver_from_faiss(self, index_path:str):
        """
        Load retriever from FAISS index.
        """

        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            
            vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization= True)
            self.retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            self.log.info("Loaded retriever from FAISS index", index_path=index_path, session_id = self.session_id)

            return self.retriever

        except Exception as e:
            self.log.error("Failed to load retriever from FAISS", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("Failed to load retriever from FAISS", sys)

    def invoke(self, user_input:str, chat_history: Optional[List[BaseMessage]] = None) -> str:
        """
        Invoke the LCEL chain with the given user input and chat history.
       """
        try:
            payload = {"input": user_input, "chat_history": chat_history or []}
            answer = self.chain.invoke(payload)
            if not answer:
                self.log.warning("Empty answer received", session_id=self.session_id)
                return "no answer generated"

            

            self.log.info("Successfully invoked ConversationalRAG Chain", 
                          session_id=self.session_id, 
                          user_input=user_input,
                          answer=answer[:150])
            return answer

        except Exception as e:
            self.log.error("Failed to invoke ConversationalRAG", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("Failed to invoke ConversationalRAG", sys)

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                raise ValueError("LLM not loaded successfully")
            self.log.info("LLM loaded successfully", session_id=self.session_id)
            return llm
        except Exception as e:
            self.log.error("Failed to load LLM", error = str(e), session_id=self.session_id)
            raise DocumentPortalException("Failed to load LLM", sys)
    
    @staticmethod
    def _format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def _build_lcel_chain(self):
        try:
            # 1) Rewrite question using chat history
            question_rewriter = (
                {"input": itemgetter("input"), "chat_history": itemgetter("chat_history")}
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )

            # 2) Retrieve docs for rewritten question
            retrieve_docs = question_rewriter | self.retriever | self._format_docs

            # 3) Feed context + original input + chat history into answer prompt
            self.chain = (
                {
                    "context": retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history"),
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )

            self.log.info("LCEL graph built successfully", session_id=self.session_id)

        except Exception as e:
            self.log.error("Failed to build LCEL chain", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("Failed to build LCEL chain", sys)