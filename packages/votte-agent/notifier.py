from notte_core.common.notifier import BaseNotifier
from typing_extensions import override

from notte_agent.common.base import BaseAgent
from notte_agent.common.types import AgentResponse


class NotifierAgent(BaseAgent):
    """Agent wrapper that sends notifications after task completion."""

    def __init__(self, agent: BaseAgent, notifier: BaseNotifier):
        super().__init__(session=agent.session)
        self.agent: BaseAgent = agent
        self.notifier: BaseNotifier = notifier

    @override
    async def run(self, task: str, url: str | None = None) -> AgentResponse:
        """Run the agent and send notification about the result."""
        result = await self.agent.run(task, url)
        self.notifier.notify(task, result)  # pyright: ignore [reportArgumentType]
        return result
