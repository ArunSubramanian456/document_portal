import os
import sys
import pandas as pd

from utils.model_loader import ModelLoader
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY 
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from model.models import SummaryResponse,PromptType


class DocumentComparerLLM:
    def __init__(self):
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()

        # Prepare Parsers
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(
            llm=self.llm,
            parser=self.parser
        )

        self.prompt = PROMPT_REGISTRY[PromptType.DOCUMENT_COMPARISON.value]
        self.chain = self.prompt | self.llm | self.parser
        log.info("DocumentComparerLLM initialized successfully")


    def compare_documents(self, combined_docs :str) -> pd.DataFrame :
        """
        Compares two documents and returns a structured comparison
        """
        try:
            inputs =  {
                "combined_docs": combined_docs,
                "format_instructions": self.parser.get_format_instructions()
            }

            log.info("Starting document comparison", inputs = inputs)
            response = self.chain.invoke(inputs)
            log.info("Document comparison completed", response = response)
            return self._format_response(response)
        
        except Exception as e:
            log.error("Document comparison failed", error=str(e))
            raise DocumentPortalException("Document comparison failed", sys)
        
    def _format_response(self, response:List[dict]) -> pd.DataFrame:
        """
        Formats the LLM response into a structured format
        """
        try:
            df = pd.DataFrame(response)
            log.info("Response formatted into Dataframe", dataframe = df)
            return df
        
        except Exception as e:
            log.error("Response formatting failed", error=str(e))
            raise DocumentPortalException("Response formatting failed", sys)


