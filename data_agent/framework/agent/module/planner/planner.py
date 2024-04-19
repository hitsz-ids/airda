from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..loader import Loader
from .pipeline.pipeline import Pipeline
from .planner_params import PlannerParams

PL = TypeVar("PL", bound=Pipeline)
PP = TypeVar("PP", bound=PlannerParams)


class Planner(ABC, Generic[PP, PL], Loader):
    @abstractmethod
    def plan(self, params: PP) -> PL:
        pass
