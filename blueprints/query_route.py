from flask import request, jsonify, Blueprint
from decouple import config
from datetime import datetime

from flask_jwt_extended import get_jwt_identity, jwt_required
from errors import handle_internal_server_error, handle_no_content
from models.conversation import Conversation
from models.messages import Message


from haystack.document_stores import PineconeDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.pipelines import GenerativeQAPipeline
from haystack.nodes import Seq2SeqGenerator

from models.user import User

query_bp = Blueprint("query", __name__)

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
BOT_ID = config("BOT_ID")


@query_bp.route("/query", methods=["POST"])
@jwt_required()
def query_fn():
    data = request.get_json()
    current_user = get_jwt_identity()
    user_id = current_user.get("id")
    user_query = data["query"]

    message = Message(
        content=user_query,
        author=user_id,
        date=datetime.now(),
    )
    message.save()

    conversation = Conversation.objects(participants__all=[user_id, BOT_ID]).first()

    if conversation:
        conversation.messages.append(message.id)
        conversation.save()

    else:
        new_conversation = Conversation(
            messages=[str(message.id)], participants=[user_id, BOT_ID]
        )
        new_conversation.save()
    try:
        result = pipe.run(
            query=user_query,
            params={"Retriever": {"top_k": 3}, "Generator": {"top_k": 1}},
        )["answers"][0].answer

        if result:
            bot_response = Message(
                content=result,
                author=BOT_ID,
                date=datetime.now(),
            )
            bot_response.save()
            conversation = Conversation.objects(
                participants__all=[user_id, BOT_ID]
            ).first()
            if conversation:
                conversation.messages.append(bot_response.id)
                conversation.save()

        else:
            return handle_no_content("Could not return suitable answer for your query")

        return jsonify({"result": result})
    except Exception as e:
        print(e)
        return handle_internal_server_error(
            "something went wrong please try again later"
        )


@query_bp.route("/queries", methods=["GET"])
@jwt_required()
def all_queries():
    current_user = get_jwt_identity()
    user_id = current_user.get("id")
    conversation = Conversation.objects(participants__all=[user_id, BOT_ID]).first()

    messages = []
    if conversation is not None:
        for message in conversation.messages:
            author = User.objects.with_id(message.author.id)
            message = {
                "_id": str(message.id),
                "author": {
                    "_id": str(author.id),
                    "name": author.name,
                    "role": author.role,
                    "display_picture": author.display_picture,
                },
                "content": message.content,
                "date": message.date,
            }
            messages.append(message)
        return jsonify({"messages": messages})
    else:
        return jsonify({"messages": []})
