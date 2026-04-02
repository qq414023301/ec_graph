from turtledemo.penrose import start

from sqlalchemy.orm import relationship
from transformers import AutoTokenizer, AutoModelForTokenClassification
from configuration.config import *
from utils import MysqlReader,Neo4jWriter
import torch
from ner.predict import Predictor


class TextSynchronizer:
    def __init__(self):
        self.reader = MysqlReader()
        self.writer = Neo4jWriter()

        self.extractor = self._init__extractor()


    #。初始化一个predictor
    def _init__extractor(self):
        model = AutoModelForTokenClassification.from_pretrained(str(CHECKPOINT_DIR / 'ner' / 'best_model'))
        tokenizer = AutoTokenizer.from_pretrained(str(CHECKPOINT_DIR / 'ner' / 'best_model'))
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        return Predictor(model, tokenizer, device)

    #同步TAG标签
    def sync_tag(self):
        # 从mysql中读取商品描述信息
        sql = """
        select id, description
        from spu_info
        """
        spu_desc = self.reader.query(sql)
        # 拆分id和描述
        ids = [item['id'] for item in spu_desc]
        descs = [item['description'] for item in spu_desc]

        # 3.提取所有商品
        tags_list = self.extractor.extract(descs)

        # for id, tags in zip(ids, tags_list):
        #     print(id,tags)

        #4.构建TAG节点的属性(id,name),以及spu->tag的关系（start_id,end_id)
        tags_properties = []
        relations = []
        for id, tags in zip(ids, tags_list):
            #遍历当前spu的每个标签
            for index, tag in enumerate(tags):
                tag_id = '-'.join([str(id), str(index)])
                property = {'id': tag_id, 'name': tag}
                tags_properties.append(property)
                #构建关系
                relation = {'start_id':id, 'end_id':tag_id}
                relations.append(relation)

            #5.写入数据库
            self.writer.write_nodes("Tag", tags_properties)
            self.writer.write_relations("Have","SPU","Tag",relations)



if __name__ == "__main__":
    synchronizer = TextSynchronizer()
    synchronizer.sync_tag()