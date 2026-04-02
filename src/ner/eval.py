import evaluate
from datasets import load_from_disk
from transformers import AutoModelForTokenClassification, Trainer, DataCollatorForTokenClassification, AutoTokenizer, \
    EvalPrediction

from configuration import config

# 1. 加载测试集
test_dataset = load_from_disk(config.DATA_DIR / 'ner' / 'processed' / 'test')

# 3. 加载模型
model = AutoModelForTokenClassification.from_pretrained(str(config.CHECKPOINT_DIR / 'ner' / 'best_model'))

# 4. 加载分词器 & data_collator
tokenizer = AutoTokenizer.from_pretrained(str(config.CHECKPOINT_DIR / 'ner' / 'best_model'))
data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer, padding=True, return_tensors='pt')

# 5. 定义评估函数
seqeval = evaluate.load("seqeval")

def compute_metrics(prediction: EvalPrediction) -> dict:
    logits = prediction.predictions
    preds = logits.argmax(axis=-1)
    labels = prediction.label_ids

    # 转换为标签名称
    true_predictions = [
        [model.config.id2label[p] for (p, l) in zip(pred, label) if l != -100]
        for pred, label in zip(preds, labels)
    ]
    true_labels = [
        [model.config.id2label[l] for (p, l) in zip(pred, label) if l != -100]
        for pred, label in zip(preds, labels)
    ]

    return seqeval.compute(predictions=true_predictions, references=true_labels)

# 6. 使用 Trainer 进行评估
trainer = Trainer(
    model=model,
    eval_dataset=test_dataset,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

metrics = trainer.evaluate()
print("评估结果", metrics)
