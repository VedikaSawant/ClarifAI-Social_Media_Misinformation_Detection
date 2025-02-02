# routes.py (Backend - Flask API)
from flask import Blueprint, request, jsonify
from app.models import get_fact_check, save_fact_check
import torch
from transformers import AutoModel, BertTokenizerFast
import torch.nn as nn
import numpy as np

api = Blueprint("api", __name__)

# Load BERT model and tokenizer (do this ONCE, outside the route function)
bert = AutoModel.from_pretrained('bert-base-uncased')
tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')

class BERT_Arch(nn.Module):
    def __init__(self, bert):
        super(BERT_Arch, self).__init__()
        self.bert = bert
        self.dropout = nn.Dropout(0.1)
        self.relu = nn.ReLU()
        self.fc1 = nn.Linear(768, 512)
        self.fc2 = nn.Linear(512, 2)  # Output layer

    def forward(self, sent_id, attention_mask):
        cls_hs = self.bert(sent_id, attention_mask=attention_mask)['pooler_output']
        x = self.fc1(cls_hs)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)  # Output layer
        return x

model = BERT_Arch(bert)
try:
    path = r'D:\ClarifAI-Social_Media_Misinformation_Detection\app\c1_fakenews_weights.pt'  # Replace with your actual path
    model.load_state_dict(torch.load(path, map_location=torch.device('cpu')), strict=False)
    print(f"Model weights loaded from: {path}") #Confirmation message
except FileNotFoundError:
    print("Model weights file not found.")
    exit()
model.eval()
cross_entropy = nn.CrossEntropyLoss()

def predict_fake_news(text_input):
    MAX_LENGHT = 15  # Consistent max length
    tokens_unseen = tokenizer.batch_encode_plus(
        [text_input],
        max_length=MAX_LENGHT,
        padding='max_length',
        truncation=True,
        return_tensors="pt"
    )
    unseen_seq = tokens_unseen['input_ids']
    unseen_mask = tokens_unseen['attention_mask']

    with torch.no_grad():
        preds = model(unseen_seq, attention_mask=unseen_mask)
        preds = preds.detach().cpu().numpy()
    preds = np.argmax(preds, axis=1)
    return preds[0]

@api.route("/api/fact-check", methods=["POST"])
def check_misinformation():
    data = request.json
    content = data.get("content")

    if not content:
        return jsonify({"error": "Content is required"}), 400

    existing_result = get_fact_check(content)
    if existing_result:
        return jsonify({
            "content": existing_result["content"],
            "verdict": existing_result["verdict"],
            "source": "database"
        }), 200

    prediction = predict_fake_news(content)
    verdict = "Fake" if prediction == 1 else "True"

    save_fact_check(content, verdict)  # This will now handle duplicates

    return jsonify({
        "content": content,
        "verdict": verdict,
        "source": "model"
    }), 200