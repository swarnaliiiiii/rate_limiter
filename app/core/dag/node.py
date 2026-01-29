from abc import ABC, abstractmethod
from app.core.contxt import RequestContext
from app.core.dag.result import NodeResult

class DecisionNode(ABC):
    @abstractmethod
    async def execute(self, ctx: RequestContext) -> NodeResult:
        pass
