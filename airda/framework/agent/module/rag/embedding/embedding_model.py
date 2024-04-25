import logging
import os
from abc import ABC, abstractmethod

import numpy as np
from transformers import AutoModel, AutoTokenizer

from airda.framework.module.immediate import Immediate

logger = logging.getLogger(__name__)


class EmbeddingModel(Immediate, ABC):
    def __init__(self) -> None:
        super().__init__()
        tokenizer = self.init_tokenizer()
        model = self.init_model()
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer, local_files_only=True)
        self.model = AutoModel.from_pretrained(model, local_files_only=True)

    @abstractmethod
    def init_tokenizer(self) -> str:
        pass

    @abstractmethod
    def init_model(self) -> str:
        pass

    @abstractmethod
    def embed_query(self, text) -> np.ndarray:
        pass
