import os
import sys
from dotenv import load_dotenv
import pandas as pd

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY 
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser


class DocumentComparerLLM:
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()

        # Prepare Parsers
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(
            llm=self.llm,
            parser=self.parser
        )

        self.prompt = PROMPT_REGISTRY["document_comparison"]
        self.chain = self.prompt | self.llm | self.parser
        self.log.info("DocumentComparerLLM initialized successfully")


    def compare_documents(self, combined_docs :str) -> pd.DataFrame :
        """
        Compares two documents and returns a structured comparison
        """
        try:
            inputs =  {
                "combined_docs": combined_docs,
                "format_instructions": self.parser.get_format_instructions()
            }

            self.log.info("Starting document comparison", inputs = inputs)
            response = self.chain.invoke(inputs)
            self.log.info("Document comparison completed", response = response)
            return self._format_response(response)
        
        except Exception as e:
            self.log.error("Document comparison failed", error=str(e))
            raise DocumentPortalException("Document comparison failed", sys)
        
    def _format_response(self, response:List[dict]) -> pd.DataFrame:
        """
        Formats the LLM response into a structured format
        """
        try:
            df = pd.DataFrame(response)
            self.log.info("Response formatted into Dataframe", dataframe = df)
            return df
        
        except Exception as e:
            self.log.error("Response formatting failed", error=str(e))
            raise DocumentPortalException("Response formatting failed", sys)


