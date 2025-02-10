from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from typing import List
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv


load_dotenv()



loader = PyPDFLoader("2405.04517v2.pdf")
data = loader.load()


text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
splits = text_splitter.split_documents(data)

 


embedding_function = OpenAIEmbeddings()
vectordb = Chroma.from_documents(
    documents=splits,
    embedding=embedding_function,
    persist_directory='./chroma'
)


llm=ChatOpenAI(model="gpt-4o",temperature=0)


# Output parser will split the LLM result into a list of queries
class LineListOutputParser(BaseOutputParser[List[str]]):
    """Output parser for a list of lines."""

    def parse(self, text: str) -> List[str]:
        lines = text.strip().split("\n")
        return list(filter(None, lines))  # Remove empty lines
    
output_parser = LineListOutputParser()



def multi_query(question: str, score_threshold: float = 0.70):

    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate three 
different versions of the given user question to retrieve relevant documents from a vector 
database. By generating multiple perspectives on the user question, your goal is to help
the user overcome some of the limitations of the distance-based similarity search. 
Provide these alternative questions separated by newlines.
Original question: {question}"""
    )
    

    llm_chain = QUERY_PROMPT | llm | output_parser
    alternative_queries = llm_chain.invoke(question)
    
    results = []
    for q in alternative_queries:
    
        docs_with_scores = vectordb.similarity_search_with_relevance_scores(q, k=2)
      
        filtered_docs = []
        for doc_tuple in docs_with_scores:
 
            document, score = doc_tuple
            if score >= score_threshold:
                filtered_docs.append((document, score))
        results.append({"query": q, "results": filtered_docs})
    return results

def generate_response(question: str):

    mq_results = multi_query(question)


    

    aggregated_context = ""
    for entry in mq_results:
        for doc, score in entry["results"]:
            aggregated_context += doc.page_content + "\n"
    
 
    RESPONSE_PROMPT = PromptTemplate(
        input_variables=["question", "documents"],
        template="""You are an AI language model assistant.
 You must strictly adhere to the context provided in the retrieved documents below and do not incorporate any external knowledge or assumptions.
Given the following question:
{question}
and the following retrieved documents:
{documents}
Generate a concise and informative answer that is entirely based on the provided context.
If the answer is not explicitly supported by the documents, state that the information is not available."""
    )
    prompt = RESPONSE_PROMPT.format(question=question, documents=aggregated_context)
    
   
    answer = llm.invoke([{"role": "human", "content": prompt}])
    return answer.content



 

    






