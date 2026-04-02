from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jGraph, Neo4jVector
from neo4j_graphrag.types import SearchType
from configuration.config import *


class IndexUtil:
    def __init__(self):
        self.graph = Neo4jGraph(
            url=str(Neo4j_CONFIG["uri"]),
            username=str(Neo4j_CONFIG["auth"][0]),
            password=str(Neo4j_CONFIG["auth"][1])
        )

        self.embed_model = HuggingFaceEmbeddings(
            model_name=os.path.expanduser("D:\\41402\\Documents\\model\\bge-small-zh-v1.5"),
            encode_kwargs={"normalize_embeddings": True},)



    # 传入索引名称， 节点标签，属性
    def create_full_text_index(self, index, label, property):
        cypher = f"""
        CREATE FULLTEXT INDEX {index} IF NOT EXISTS
        FOR (n:{label})
        ON EACH [n.{property}]
        """
        self.graph.query(cypher, {'index': index, 'label': label, 'property': property})

    def create_vector_index(self, index, label, source_property, embedding_property):
        #生成向量嵌入，并添加到节点属性中
        embedding_dim = self._add_embedding(label, source_property, embedding_property)


        # 生成嵌入向量，并添加到节点属性中
        cypher = f"""
        CREATE VECTOR INDEX {index} IF NOT EXISTS
        FOR (n:{label})
        ON n.{embedding_property}
        OPTIONS{{ indexConfig:{{
        `vector.dimensions`:{embedding_dim},
        `vector.similarity_function`: 'cosine'
        }}
        }}
        """
        self.graph.query(cypher)

    #返回向量维度
    def _add_embedding(self, label, source_property, embedding_property):
        #1. 查询所有节点对应的源属性值，作为模型输入，查出节点id
        cypher = f"""
            MATCH (n:{label})
            RETURN n.{source_property} as text, id(n) as id
        """
        results = self.graph.query(cypher)

        #2. 获取查询结果中的文本
        docs = [result['text'] for result in results]

        #3. 调用嵌入模型，得到嵌入向量
        embeddings = self.embed_model.embed_documents(docs)

        #4. 将id和嵌入向量组合成字典形式
        batch = []
        for result, embedding in zip(results, embeddings):
            item = {'id': result['id'], 'embedding': embedding}
            batch.append(item)

        #5. 执行cypher，按id查节点，写入新的嵌入向量属性
        cypher = f"""
            UNWIND $batch AS item
            MATCH (n:{label})
            WHERE id(n) = item.id
            SET n.{embedding_property} = item.embedding
        """
        self.graph.query(cypher, {'batch': batch})
        return len(embeddings[0])



if __name__ == '__main__':
    index = IndexUtil()
    index.create_full_text_index("trademark_fulltext_index", "Trademark", "name")
    index.create_vector_index("trademark_vector_index", "Trademark", "name","embedding")


    index_name="trademark_vector_index"
    keyword_index_name="trademark_fulltext_index"

    store = Neo4jVector.from_existing_index(
        index.embed_model,
        url=str(Neo4j_CONFIG["uri"]),
        username=str(Neo4j_CONFIG["auth"][0]),
        password=str(Neo4j_CONFIG["auth"][1]),
        index_name = index_name,
        keyword_index_name = keyword_index_name,
        search_type = SearchType.HYBRID,
    )
    result = store.similarity_search("apple",5)

    index.create_full_text_index("spu_fulltext_index", "SPU", "name")
    index.create_vector_index("spu_vector_index", "SPU", "name","embedding")
    index.create_full_text_index("sku_fulltext_index", "SKU", "name")
    index.create_vector_index("sku_vector_index", "SKU", "name","embedding")

    index.create_full_text_index("category1_fulltext_index", "Category1", "name")
    index.create_vector_index("category1_vector_index", "Category1", "name", "embedding")

    index.create_full_text_index("category2_fulltext_index", "Category2", "name")
    index.create_vector_index("category2_vector_index", "Category2", "name", "embedding")

    index.create_full_text_index("category3_fulltext_index", "Category3", "name")
    index.create_vector_index("category3_vector_index", "Category3", "name", "embedding")