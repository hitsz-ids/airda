from pydantic import BaseModel

from data_agent.framework.agent.module.planner.pipeline.pipeline_params import (
    PipelineParams,
)
from data_agent.framework.agent.module.planner.planner_params import PlannerParams


class DataAgentPlannerParams(BaseModel, PlannerParams, PipelineParams):
    question: str
