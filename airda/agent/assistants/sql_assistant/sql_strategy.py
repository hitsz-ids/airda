from abc import ABC, abstractmethod
from typing import Generic

from overrides import overrides

from airda.agent.action.explainer import ExplainerParams
from airda.agent.action.searcher import Searcher, SearcherParams
from airda.agent.action.sql_generator import SqlGenerator, SQLGeneratorParams
from airda.framework.action.action import Action, P


class SQLStrategy(ABC, Generic[P]):
    @abstractmethod
    def concat(self, params: P, previous: dict[type[Action], Action]):
        pass


class SearcherStrategy(SQLStrategy[SearcherParams]):
    @overrides
    def concat(self, params: SearcherParams, previous: dict[type[Action], Action]):
        pass


class SQLGeneratorStrategy(SQLStrategy[SQLGeneratorParams]):
    @overrides
    def concat(self, params: SQLGeneratorParams, previous: dict[type[Action], Action]):
        if previous:
            previous_action = previous[Searcher]
            if previous_action:
                params.searcher_result = previous_action.get_result


class ExplainerStrategy(SQLStrategy[ExplainerParams]):
    @overrides
    def concat(self, params: ExplainerParams, previous: dict[type[Action], Action]):
        if previous and len(previous) > 0:
            for i in previous:
                previous_action = previous[i]
                if isinstance(previous_action, Searcher):
                    params.searcher_result = previous_action.get_result
                if isinstance(previous_action, SqlGenerator):
                    params.generator_result = previous_action.get_result
