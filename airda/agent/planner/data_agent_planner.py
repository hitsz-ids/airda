from airda.agent.planner.data_agent_pipeline import DataAgentPipeline
from airda.agent.planner.data_agent_planner_params import DataAgentPlannerParams
from airda.framework.agent.module.planner.planner import Planner


class DataAgentPlanner(Planner[DataAgentPlannerParams, DataAgentPipeline]):
    def plan(self, params: DataAgentPlannerParams) -> DataAgentPipeline:
        return DataAgentPipeline(params, self.context)
