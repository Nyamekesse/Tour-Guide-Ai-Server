from flask import jsonify, request, Blueprint
import pandas as pd
from transformers import pipeline, AutoTokenizer

from errors import handle_not_processable_error


model = f"cardiffnlp/twitter-roberta-base-sentiment-latest"

tokenizer = AutoTokenizer.from_pretrained(model)
sentiment_task = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    max_length=512,
    truncation=True,
)

sentiment_bp = Blueprint("sentiment", __name__)


@sentiment_bp.route("/sentiment", methods=["POST"])
def sentiment_analysis():
    if "file" not in request.files:
        return "No file part"
    file = request.files["file"]
    df = pd.read_csv(file, sep="|")
    if df.shape[0] > 200:
        return handle_not_processable_error("The CSV file should not exceed 200 rows")
    df["sentiment"] = df["reviews"].apply(lambda x: sentiment_task(x)[0]["label"])

    results = df.to_json(orient="records")

    return jsonify({"result": results})
