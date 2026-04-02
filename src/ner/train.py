import time

from datasets import load_dataset, load_from_disk
from transformers import AutoModelForTokenClassification, Trainer, TrainingArguments, EvalPrediction, \
    DataCollatorForTokenClassification, AutoTokenizer
import evaluate

from configuration.config import *
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['TENSORBOARD_LOGGING_DIR'] = str(LOG_DIR / NER_DIR / time.strftime("%Y-%m-%d-%H-%M-%S"))

#1. 分词器
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

#标签映射
id2label = {id: label for id, label in enumerate(LABELS)}
label2id = {label: id for id, label in enumerate(LABELS)}


#2. 模型
model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME,
                                                        num_labels=len(LABELS),
                                                        id2label=id2label,
                                                        label2id=label2id)

#3. 加载数据集
train_dataset = load_from_disk(PROCESSED_DATA_DIR/'train')
validation_dataset = load_from_disk(PROCESSED_DATA_DIR/'valid')

#4. 数据整理器
data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer,
                                                   padding=True,
                                                   return_tensors='pt')

# 训练参数
args = TrainingArguments(output_dir=str(CHECKPOINT_DIR / 'ner'),  # 模型保存目录
                         report_to=['tensorboard'],  # 日志目录
                         per_device_train_batch_size=2,  # 训练批次大小
                         logging_steps=SAVE_STEPS,  # 训练日志间隔
                         num_train_epochs=EPOCHS,  # 训练轮数
                         save_steps=20,  # 模型保存间隔
                         save_total_limit=3,  # 最多保存模型数量
                         eval_strategy='steps',  # 评估策略
                         eval_steps=20,  # 评估间隔
                         load_best_model_at_end=True,  # 训练结束加载最优模型
                         metric_for_best_model='eval_overall_f1',  # 最优模型评估指标
                         greater_is_better=True,
                         logging_strategy='steps',
                         logging_first_step=True,

                        )

# 评估指标函数
seqeval = evaluate.load("seqeval")

def compute_metrics(predictions:EvalPrediction):
    #提取模型的预测输出和真实标签
    logits = predictions.predictions
    preds = logits.argmax(axis=-1) #预测标签
    labels = predictions.label_ids #真实标签

    #将标签id转换为真正的标注标签BIO
    unpad_labels = []
    unpad_preds = []
    for pred,label in zip(preds,labels):
        unpad_label = label[label!=-100]
        unpad_pred = pred[label!=-100]
        #转BIO标签
        unpad_pred = [id2label[id] for id in unpad_pred]
        unpad_label = [id2label[id] for id in unpad_label]
        #添加到列表
        unpad_labels.append(unpad_label)
        unpad_preds.append(unpad_pred)

    result = seqeval.compute(predictions=unpad_preds,references=unpad_labels)
    return result

#4. 创建训练器
trainer = Trainer(model=model,
                  args=args,
                  data_collator=data_collator,
                  train_dataset=train_dataset,
                  eval_dataset=validation_dataset,
                  compute_metrics=compute_metrics)

#训练
trainer.train()

#模型保存
trainer.save_model(CHECKPOINT_DIR/NER_DIR/'best_model')

