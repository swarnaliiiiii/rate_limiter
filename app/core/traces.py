from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class TraceStep:
    node: str
    outcome: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionTrace:
    steps: List[TraceStep] = field(default_factory=list)

    def add(self, node: str, outcome: str, **metadata):
        self.steps.append(
            TraceStep(
                node=node,
                outcome=outcome,
                metadata=metadata
            )
        )
