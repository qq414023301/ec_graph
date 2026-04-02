from datasets import load_dataset
from transformers import AutoTokenizer
from configuration.config import *
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
def preprocess():
    #1. 读数据
    dataset = load_dataset('json',data_files=RAW_DATA_FILE)['train']
    # print(dataset)

    #2. 去除多余列
    dataset.remove_columns(['id', 'annotator', 'annotation_id', 'created_at', 'updated_at', 'lead_time'])

    #3. 划分数据集
    dataset_dict = dataset.train_test_split(train_size=0.8)
    dataset_dict['test'], dataset_dict['valid'] = dataset_dict['test'].train_test_split(test_size=0.5).values()

    #4. 定义分词器
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    #5. 数据编码
    def encode(example):
        #5.1 将文本数据转成字符串列表
        tokens = list(example['text'])
        #5.2 文本编码
        inputs = tokenizer(tokens, is_split_into_words=True, truncation=True)
        #5.3 实体标注
        entities = example['label']
        #5.4 定义标注列表,存放id，默认都为‘O’的id
        labels = [LABELS.index('O')] * len(tokens)
        #5.5 遍历2每个TAG，标记为B和I的id
        for entity in entities:
            start = entity['start']
            end = entity['end']
            labels[start:end] =  [LABELS.index('B')] + [LABELS.index('I')] * (end - start -1)
        # 前后加上id=-100
        labels = [-100] + labels + [-100]
        inputs['labels'] = labels
        return inputs

    dataset_dict = dataset_dict.map(encode, remove_columns=['text','label'])

    #5. 保存文件
    dataset_dict.save_to_disk(PROCESSED_DATA_DIR)



if __name__ == "__main__":
    preprocess()