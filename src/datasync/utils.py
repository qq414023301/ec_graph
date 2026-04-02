import pymysql
from PIL.Image import item
from click.core import batch
from neo4j import GraphDatabase
from pymysql.cursors import DictCursor
from sqlalchemy.orm import relationship

from configuration.config import *

class MysqlReader:
    def __init__(self):
        self.connection = pymysql.connect(**MySQL_CONFIG)
        self.cursor = self.connection.cursor(DictCursor)

    def query(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    #关闭连接

    def close(self):
        self.cursor.close()
        self.connection.close()

class Neo4jWriter:
    def __init__(self):
        self.driver = GraphDatabase.driver(**Neo4j_CONFIG)

    #写入节点
    def write_nodes(self, label:str, properties:list[dict]):
        cypher = f"""
            UNWIND $batch AS item
            MERGE (:{label} {{id:item.id, name:item.name}})        
            """
        self.driver.execute_query(cypher, batch=properties)

    # 写入关系
    def write_relations(self, type: str, start_label, end_label, relations: list[dict]):
        cypher = f"""
             UNWIND $batch AS item
             MATCH (start:{start_label} {{id:item.start_id}}),(end:{end_label} {{id:item.end_id}})          
             MERGE (start)-[:{type}]->(end)        
             """
        self.driver.execute_query(cypher, batch=relations)

