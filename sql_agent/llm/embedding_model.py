import logging
import os

import numpy as np
from sklearn.preprocessing import normalize
from transformers import AutoModel, AutoTokenizer

logger = logging.getLogger(__name__)


class EmbeddingModel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmbeddingModel, cls).__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        model_name = os.getenv("EMBEDDINGS_MODEL_NAME", "infgrad/stella-large-zh-v2")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, local_files_only=True
            )
        except Exception as e:
            logger.error(f"加载tokenizer错误:{e}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, local_files_only=True
            )
        try:
            self.model = AutoModel.from_pretrained(model_name, local_files_only=True)
        except Exception as e:
            logger.error(f"加载model错误:{e}")
            self.model = AutoModel.from_pretrained(model_name, local_files_only=True)

    def embed_query(self, text) -> np.ndarray:
        if isinstance(text, str):
            text = [text]
        try:
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

        except Exception as e:
            logger.info(f"Error in generating embeddings: {e}")
            return np.array([])  # Returning empty array in case of an error
