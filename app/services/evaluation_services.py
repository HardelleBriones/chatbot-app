import chromadb
from llama_index.core import (
    VectorStoreIndex,
)
from llama_index.core.schema import BaseNode
from typing import List
from llama_index.core import MockEmbedding
from llama_index.core.llms import MockLLM
import tiktoken

from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler

from dotenv import load_dotenv
load_dotenv()
def file_cost_embeddings(documents: List[BaseNode]):
    embed_model = MockEmbedding(embed_dim=1536)
    token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
    )   
    callback_manager = CallbackManager([token_counter])
    embed_model = embed_model
    VectorStoreIndex(documents,embed_model=embed_model,callback_manager=callback_manager)
    return token_counter.total_embedding_token_count