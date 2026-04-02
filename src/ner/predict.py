
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

from configuration import config

class Predictor:
    def __init__(self, model, tokenizer, device):
        self.model = model.to(device)
        self.model.eval()
        self.tokenizer = tokenizer
        self.device = device

    def predict(self, inputs: str | list, batch_size=8):
        is_str = isinstance(inputs, str)
        if is_str:
            inputs = [inputs]

        predictions = []
        for i in range(0, len(inputs), batch_size):
            batch = inputs[i:i + batch_size]
            batch = [list(text) for text in batch]
            batch_inputs = self.tokenizer(batch, return_tensors="pt",
                                          padding=True, truncation=True, is_split_into_words=True)
            batch_inputs = {k: v.to(self.device) for k, v in batch_inputs.items()}
            with torch.no_grad():
                outputs = self.model(**batch_inputs)
                logits = outputs.logits
                batch_preds = torch.argmax(logits, dim=-1).tolist()

            for text, pred in zip(batch, batch_preds):
                pred = pred[1:1 + len(text)]
                pred = [self.model.config.id2label[id] for id in pred]
                predictions.append(pred)

        if is_str:
            predictions = predictions[0]
        return predictions

    def extract(self, inputs: str | list):
        is_str = isinstance(inputs, str)
        if is_str:
            inputs = [inputs]

        inputs = [text.replace(" ", "") for text in inputs]

        results = self.predict(inputs)

        all_entities = []
        for text, pred in zip(inputs, results):
            entities = self._bio_to_entities(text, pred)
            all_entities.append(entities)

        if is_str:
            return all_entities[0]
        return all_entities

    def _bio_to_entities(self, tokens, labels):
        """
        只提取连续的 B-I 序列为实体
        - 遇到 B 开始新实体
        - 遇到 I 接续实体
        - 遇到 O 或 I 前没有 B 时结束实体
        """
        entities = []
        entity = ""

        for token, label in zip(tokens, labels):
            if label == "B":
                if entity:
                    entities.append(entity)
                entity = token
            elif label == "I":
                if entity:  # 只有前面有 B 才接续
                    entity += token
                else:
                    # I 前没有 B，直接跳过
                    continue
            else:  # O
                if entity:
                    entities.append(entity)
                    entity = ""

        if entity:
            entities.append(entity)

        return entities

if __name__ == '__main__':
    model = AutoModelForTokenClassification.from_pretrained(str(config.CHECKPOINT_DIR / 'ner' / 'best_model'))
    tokenizer = AutoTokenizer.from_pretrained(str(config.CHECKPOINT_DIR / 'ner' / 'best_model'))
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    predictor = Predictor(model, tokenizer, device)
    inputs = ["2018秋冬季新款韩版平底高帮鞋女休闲二棉鞋加绒运动厚底高邦鞋潮",
              "2018秋冬季新款韩版平底高帮鞋女休闲二棉鞋加绒运动厚底高邦鞋潮"]
    result = predictor.extract(inputs)
    print(result)
