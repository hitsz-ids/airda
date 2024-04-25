import numpy as np
from sklearn.preprocessing import normalize

from airda.agent.env import DataAgentEnv
from airda.framework.agent.module.rag.embedding.embedding_model import (
    EmbeddingModel,
)


class DataAgentEmbeddingModel(EmbeddingModel):
    def init_tokenizer(self):
        return DataAgentEnv().get("embeddings_model_name")

    def init_model(self) -> str:
        return DataAgentEnv().get("embeddings_model_name")

    def embed_query(self, text) -> np.ndarray:
        if isinstance(text, str):
            text = [text]
        # Tokenization
        inputs = self.tokenizer(
            text=text,
            padding="longest",
            return_tensors="pt",
            max_length=1024,
            truncation=True,
        )
        # Model inference
        model_output = self.model(**inputs)

        attention_mask = inputs["attention_mask"]
        last_hidden = model_output.last_hidden_state.masked_fill(
            ~attention_mask[..., None].bool(), 0.0
        )

        # Generating embeddings
        embeddings = []
        for idx in range(last_hidden.shape[0]):
            embeddings.append(
                normalize(
                    last_hidden[idx].detach().cpu().numpy(),
                    norm="l2",
                    axis=1,
                )
            )
        return np.array(embeddings)
