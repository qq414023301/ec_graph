from utils import MysqlReader,Neo4jWriter

# 构建一个表数据同步器
class TableSynchronizer:
    def __init__(self):
        self.reader = MysqlReader()
        self.writer = Neo4jWriter()

    def sync_category1(self):
        sql = """
              select id, name
              from base_category1 
              """
        # 读取mysqlm,得到属性
        properties = self.reader.query(sql)
        # 向neo4j写入节点
        self.writer.write_nodes("Category1", properties)

    def sync_category2(self):
        sql = """
              select id, name
              from base_category2 
              """
        # 读取mysqlm,得到属性
        properties = self.reader.query(sql)
        # 向neo4j写入节点
        self.writer.write_nodes("Category2", properties)

    def sync_category3(self):
        sql = """
              select id, name
              from base_category3 
              """
        # 读取mysqlm,得到属性
        properties = self.reader.query(sql)
        # 向neo4j写入节点
        self.writer.write_nodes("Category3", properties)

    def sync_category2_to_category1(self):
        sql = """
              select id start_id,
                     category1_id end_id
              from base_category2 
              """
        # 读取mysqlm,得到属性
        relations = self.reader.query(sql)
        # 向neo4j写入节点
        self.writer.write_relations("Belong", "Category2", "Category1", relations)

    def sync_category3_to_category2(self):
        sql = """
              select id start_id,
                     category2_id 
                     end_id
              from base_category3 
              """
        # 读取mysqlm,得到属性
        relations = self.reader.query(sql)
        # 向neo4j写入节点
        self.writer.write_relations("Belong", "Category3", "Category2", relations)

    #2. 平台属性
    def sync_base_attr_name(self):
        sql = """
                select id, attr_name name
              from base_attr_info
        """
        properties = self.reader.query(sql)
        # 向neo4j写入节点
        self.writer.write_nodes("BaseAttrName", properties)

    def sync_base_attr_value(self):
        sql = """
              select id, value_name name
              from base_attr_value 
              """
        properties = self.reader.query(sql)
        # 向neo4j写入节点
        self.writer.write_nodes("BaseAttrValue", properties)

    def sync_base_attr_name_to_value(self):
        sql = """
              select id end_id,
                  attr_id start_id
              from base_attr_value 
              """
        relations = self.reader.query(sql)
        # 向neo4j写入节点
        self.writer.write_relations("Have", "BaseAttrName", "BaseAttrValue", relations)

    def sync_category1_to_base_attr_name(self):
        # 利用category_level进行过滤
        sql = """
            select  category_id start_id,
                id  end_id
            from base_attr_info 
            where category_level = 1
        """
        relations = self.reader.query(sql)
        self.writer.write_relations("Have", "Category1", "BaseAttrName", relations)

    def sync_category2_to_base_attr_name(self):
        # 利用category_level进行过滤
        sql = """
              select category_id start_id, 
                     id          end_id
              from base_attr_info
              where category_level = 2 
              """
        relations = self.reader.query(sql)
        self.writer.write_relations("Have", "Category2", "BaseAttrName", relations)

    def sync_category3_to_base_attr_name(self):
        # 利用category_level进行过滤
        sql = """
              select category_id start_id, \
                     id          end_id
              from base_attr_info
              where category_level = 3 \
              """
        relations = self.reader.query(sql)
        self.writer.write_relations("Have", "Category3", "BaseAttrName", relations)


    #3. 商品信息
    def sync_spu(self):
        sql = """
            select id,
                spu_name name
            from spu_info
        """
        properties = self.reader.query(sql)
        self.writer.write_nodes("SPU", properties)


    def sync_sku(self):
        sql = """
            select id,
                sKu_name name
            from sku_info
        """
        properties = self.reader.query(sql)
        self.writer.write_nodes("SKU", properties)

    def sync_sku_to_spu(self):
        sql = """
            select id start_id,
                spu_id end_id
            from sku_info
        """
        relations = self.reader.query(sql)
        self.writer.write_relations("Belong", "SKU","SPU",relations)

    def sync_spu_to_categoty3(self):
        sql = """
            select id start_id,
                category3_id end_id
            from spu_info
        """
        relations = self.reader.query(sql)
        self.writer.write_relations("Belong", "SPU","Category3",relations)

    # 品牌信息
    def sync_trademark(self):
        sql = """
        select id,
            tm_name name
        from base_trademark
        """
        properties = self.reader.query(sql)
        self.writer.write_nodes("Trademark", properties)

    def sync_spu_to_trademark(self):
        sql = """
        select id start_id,
            tm_id end_id
        from spu_info
        """
        relations = self.reader.query(sql)
        self.writer.write_relations("Belong","SPU","Trademark", relations)


    #5. 销售属性
    def sync_sale_attr_name(self):
        sql = """
            select id,
                   sale_attr_name name
            from spu_sale_attr
        """
        properties = self.reader.query(sql)
        self.writer.write_nodes("SaleAttrName", properties)

    def sync_sale_attr_value(self):
        sql = """
            select id,
                sale_attr_value_name name
            from spu_sale_attr_value
        """
        properties = self.reader.query(sql)
        self.writer.write_nodes("SaleAttrValue", properties)

    def sync_sale_attr_name_to_value(self):
        sql = """
        select a.id start_id,
            v.id end_id
        from spu_sale_attr a
            join spu_sale_attr_value v 
            on a.spu_id = v.spu_id
            and a.base_sale_attr_id = v.base_sale_attr_id
        """
        relations = self.reader.query(sql)
        self.writer.write_relations("Have", "SaleAttrName","SaleAttrValue",relations)

    def sync_spu_to_sale_attr_name(self):
        sql="""
        select spu_id start_id,
            id end_id
        from spu_sale_attr
        """
        relations = self.reader.query(sql)
        self.writer.write_relations("Have", "SPU", "SaleAttrName", relations)


    def sync_sku_to_sale_attr_value(self):
        sql="""
            select sku_id start_id,
                sale_attr_value_id end_id
            from sku_sale_attr_value
        """
        relations = self.reader.query(sql)
        self.writer.write_relations("Have", "SKU", "SaleAttrValue", relations)

    def sync_sku_to_base_attr_value(self):
        sql="""
            select sku_id start_id,
                value_id end_id
            from sku_attr_value
        """
        relations = self.reader.query(sql)
        self.writer.write_relations("Have", "SKU", "BaseAttrValue", relations)


if __name__ == "__main__":
    synchronizer = TableSynchronizer()
    # 1. 同步分类器
    synchronizer.sync_category1()
    synchronizer.sync_category2()
    synchronizer.sync_category3()
    synchronizer.sync_category2_to_category1()
    synchronizer.sync_category3_to_category2()

    #2. 同步平台属性
    synchronizer.sync_base_attr_name()
    synchronizer.sync_base_attr_value()
    synchronizer.sync_base_attr_name_to_value()
    synchronizer.sync_category1_to_base_attr_name()
    synchronizer.sync_category2_to_base_attr_name()
    synchronizer.sync_category3_to_base_attr_name()


    #3. 同步商品信息
    synchronizer.sync_spu()  # 先同步父节点
    synchronizer.sync_sku()
    synchronizer.sync_sku_to_spu()
    synchronizer.sync_spu_to_categoty3()

    #同步品牌信息
    synchronizer.sync_trademark()
    synchronizer.sync_spu_to_trademark()

    #同步销售属性相关信息

    synchronizer.sync_sale_attr_name()
    synchronizer.sync_sale_attr_value()
    synchronizer.sync_sale_attr_name_to_value()
    synchronizer.sync_spu_to_sale_attr_name()
    synchronizer.sync_sku_to_base_attr_value()
    synchronizer.sync_sku_to_sale_attr_value()