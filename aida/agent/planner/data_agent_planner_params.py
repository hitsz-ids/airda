from pydantic import BaseModel

from aida.framework.agent.module.planner.pipeline.pipeline_params import (
    PipelineParams,
)
from aida.framework.agent.module.planner.planner_params import PlannerParams


class DataAgentPlannerParams(BaseModel, PlannerParams, PipelineParams):
    question: str
