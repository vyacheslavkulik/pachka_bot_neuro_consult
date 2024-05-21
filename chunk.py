import os
import requests
import re

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.docstore.document import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv


# получим переменные окружения из .env
load_dotenv()

class Chunk():
    # API-key
    llm = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), model="gpt-4o", temperature=0.1)

    def __init__(self, path_to_base:str, ch_size:int=1024):

        # Extract the document ID from the URL
        match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', path_to_base)
        if match_ is None:
            raise ValueError('Invalid Google Docs URL')
        doc_id = match_.group(1)

        # Download the document as plain text
        response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
        response.raise_for_status()
        text = response.text



        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
        ]

        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        fragments = markdown_splitter.split_text(text)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=ch_size,
            chunk_overlap=0,
        )

        source_chunks = [
            Document(page_content=chunk, metadata=fragment.metadata)
            for fragment in fragments
            for chunk in splitter.split_text(fragment.page_content)
        ]

        # создаем индексную базу
        embeddings = OpenAIEmbeddings()
        self.db = FAISS.from_documents(source_chunks, embeddings)
    

    async def async_get_answer(self, query:str = None):
    #def async_get_answer(self, query:str = None):
        """Асинхронная функция получения ответа от chatgpt

        Args:
            query (str, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """        
        # задаем system

        system = "Ты консультант в компании который следит за базой знаний компании, ответь на вопрос клиента на основе документа с информацией. Не придумывай ничего от себя, отвечай максимально по документу. Не упоминай Документ с информацией для ответа клиенту. Клиент ничего не должен знать про Документ с информацией для ответа клиенту"

        # релевантные отрезки из базы
        # docs = self.db.similarity_search(query, k=4)
        docs = self.db.similarity_search_with_score(query, k=7)
        filtered_docs = [(doc, score) for doc, score in docs if score < 0.35]
        scores = [str(score) for _, score in docs]
        message_content = '\n'.join([f'{doc[0].page_content}' for doc in filtered_docs])
        
        print(scores)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("user", "{input}")
        ])
        output_parser = StrOutputParser() # конвертация ответа в строку

        chain = prompt | self.llm | output_parser 

        print(message_content)
        answer = chain.invoke({"input": f"Ответь на вопрос клиента. Не упоминай документ с информацией для ответа клиенту в ответе. Документ с информацией для ответа клиенту: {message_content}\n\nВопрос клиента: \n{query}"})
        
        return answer