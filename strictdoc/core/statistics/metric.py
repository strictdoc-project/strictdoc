from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Metric:
    name: str
    value: str
    link: Optional[str] = None


@dataclass
class MetricSection:
    name: str
    metrics: List[Metric]
