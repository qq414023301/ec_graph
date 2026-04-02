from typing import Dict, List, Any

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jGraph, Neo4jVector
from neo4j_graphrag.types import SearchType
from configuration.config import *
import dotenv
dotenv.load_dotenv()
import os

class ChatService:
    def __init__(self):
        self.graph = Neo4jGraph(
            url=str(Neo4j_CONFIG["uri"]),
            username=str(Neo4j_CONFIG["auth"][0]),
            password=str(Neo4j_CONFIG["auth"][1])
        )

        self.embed_model = HuggingFaceEmbeddings(
            model_name=os.path.expanduser("D:\\41402\\Documents\\model\\bge-small-zh-v1.5"),
            encode_kwargs={"normalize_embeddings": True},)

        self.llm = ChatDeepSeek(model='deepseek-chat', api_key=os.getenv("DEEPSEEK_API_KEY"))

        self.neo4j_vectors = {
            'SPU': Neo4jVector.from_existing_index(
                self.embed_model,
                url=Neo4j_CONFIG['uri'],
                username=str(Neo4j_CONFIG["auth"][0]),
                password=str(Neo4j_CONFIG["auth"][1]),
                index_name='spu_vector_index',
                keyword_index_name='spu_fulltext_index',
                search_type=SearchType.HYBRID
            ),
            'SKU': Neo4jVector.from_existing_index(
                self.embed_model,
                url=Neo4j_CONFIG['uri'],
                username=str(Neo4j_CONFIG["auth"][0]),
                password=str(Neo4j_CONFIG["auth"][1]),
                index_name='sku_vector_index',
                keyword_index_name='sku_fulltext_index',
                search_type=SearchType.HYBRID
            ),
            'Trademark': Neo4jVector.from_existing_index(
                self.embed_model,
                url=str(Neo4j_CONFIG["uri"]),
                username=str(Neo4j_CONFIG["auth"][0]),
                password=str(Neo4j_CONFIG["auth"][1]),
                index_name='trademark_vector_index',
                keyword_index_name='trademark_fulltext_index',
                search_type=SearchType.HYBRID
            ),
            'Category3': Neo4jVector.from_existing_index(
                self.embed_model,
                url=Neo4j_CONFIG['uri'],
                username=str(Neo4j_CONFIG["auth"][0]),
                password=str(Neo4j_CONFIG["auth"][1]),
                index_name='category3_vector_index',
                keyword_index_name='category3_fulltext_index',
                search_type=SearchType.HYBRID
            ),
            'Category2': Neo4jVector.from_existing_index(
                self.embed_model,
                url=Neo4j_CONFIG['uri'],
                username=str(Neo4j_CONFIG["auth"][0]),
                password=str(Neo4j_CONFIG["auth"][1]),
                index_name='category2_vector_index',
                keyword_index_name='category2_fulltext_index',
                search_type=SearchType.HYBRID
            ),
            'Category1': Neo4jVector.from_existing_index(
                self.embed_model,
                url=Neo4j_CONFIG['uri'],
                username=str(Neo4j_CONFIG["auth"][0]),
                password=str(Neo4j_CONFIG["auth"][1]),
                index_name='category1_vector_index',
                keyword_index_name='category1_fulltext_index',
                search_type=SearchType.HYBRID
            )
        }

        self.json_parser = JsonOutputParser()
        self.str_parser = StrOutputParser()

    def _generate_cypher(self, question: str, schema_info: str):
        generate_cypher_prompt = PromptTemplate(
            input_variables=["question", "schema_info"],
            template="""
                你是一个专业的Neo4j Cypher查询生成器。你的任务是根据用户问题生成一条Cypher查询语句，用于从知识图谱中获取回答用户问题所需的信息。

                用户问题：{question}

                知识图谱结构信息：{schema_info}

                要求：
                1. 生成参数化Cypher查询语句，用param_0, param_1等代替具体值
                2. 识别需要对齐的实体
                3. 必须严格使用以下JSON格式输出结果
                {{
                  "cypher_query": "生成的Cypher语句",
                  "entities_to_align": [
                    {{
                      "param_name": "param_0",
                      "entity": "原始实体名称",
                      "label": "节点类型"
                    }}
                  ]
                }}"""
        ).format(schema_info=schema_info, question=question)
        cypher = self.llm.invoke(generate_cypher_prompt)
        cypher = self.json_parser.invoke(cypher)
        return cypher

    def _entity_align(self, entities_to_align):
        """使用向量+关键词检索修正实体名称"""
        for index, node in enumerate(entities_to_align):
            label = node['label']
            entity = node['entity']

            align_entity = self.neo4j_vectors[label].similarity_search(entity, k=1)[0].page_content
            entities_to_align[index]['entity'] = align_entity
        return entities_to_align

    def _execute_cypher(self, cypher, aligned_entities ):
        """执行 Cypher 查询并返回结果"""
        params = {aligned_entity['param_name']: aligned_entity['entity'] for aligned_entity in aligned_entities}
        results = self.graph.query(cypher, params=params)
        return results

    def _generate_answer(self, question, query_result):
        """
        将 Cypher 查询结果生成自然语言答案
        """
        prompt = PromptTemplate(
            input_variables=["question", "query_result"],
            template="""
                你是一个电商智能客服，根据用户问题，以及数据库查询结果生成一段简洁、准确的自然语言回答。
                用户问题: {question}
                数据库返回结果: {query_result}
            """).format(question=question, query_result=query_result)
        result = self.llm.invoke(prompt)
        return self.str_parser.invoke(result)

    def chat(self, question: str):
        #根据用户问题生成cypher以及需要对齐的实体
        cypher = self._generate_cypher(question, self.graph.schema)
        cypher_query = cypher['cypher_query']
        entities_to_align = cypher['entities_to_align']
        entities = self._entity_align(entities_to_align)
        query_result = self._execute_cypher(cypher_query, entities)
        answer =  self._generate_answer(question, query_result)
        print(answer)
        return answer

if __name__ == '__main__':
    chat_service = ChatService()
    chat_service.chat("apple都有哪些产品")