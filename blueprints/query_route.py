from flask import request, jsonify, Blueprint


query_bp = Blueprint("query", __name__)

from haystack.document_stores import PineconeDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.pipelines import GenerativeQAPipeline
from haystack.nodes import Seq2SeqGenerator


document_store = PineconeDocumentStore(
    api_key="c86db173-3f02-478f-9892-471ff99763d0",
    index="project-work",
    similarity="cosine",
    embedding_dim=768,
    environment="us-east1-gcp",
)

retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="flax-sentence-embeddings/all_datasets_v3_mpnet-base",
    model_format="sentence_transformers",
)


generator = Seq2SeqGenerator(model_name_or_path="vblagoje/bart_lfqa")


pipe = GenerativeQAPipeline(generator, retriever)

@query_bp.route("/query", methods=["POST"])
def query_fn():
    data = request.get_json()

    result = pipe.run(
        query=data["query"],
        params={"Retriever": {"top_k": 3}, "Generator": {"top_k": 1}},
    )["answers"][0].answer

    return jsonify({"result": result})
