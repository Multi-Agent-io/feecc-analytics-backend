from aioprometheus.collectors import Counter
from loguru import logger
import re

from modules.singleton import SingletonMeta


class Metrics(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._metrics: dict[str, Counter] = {}

    @staticmethod
    def _transform(text: str) -> str:
        """Convert camel/pascal case to snake_case"""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()

    def _create(self, name: str, description: str) -> None:
        """Create metric"""
        self._metrics[name] = Counter(name=self._transform(name), doc=description)

    def register(self, name: str, description: str | None, labels: dict[str, str] = {}) -> None:
        """Register metric event"""
        if name not in self._metrics:
            self._create(name=name, description=description or "")
        self._metrics[name].inc(labels)
