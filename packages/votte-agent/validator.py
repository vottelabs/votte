from typing import final

import chevron
from notte_core.actions import CompletionAction
from notte_core.browser.observation import Observation
from notte_core.llms.engine import LLMEngine
from pydantic import BaseModel

from notte_agent.common.conversation import Conversation
from notte_agent.common.perception import BasePerception
from notte_agent.common.trajectory_history import TrajectoryHistory

system_rules = """
You are a validator of an agent who interacts with a browser.
Validate if the output of last action is what the user wanted and if the task is completed.
If the task is unclear defined, you can let it pass.
But if something is missing or the image does not show what was requested dont let it pass.
Try to understand the page and help the model with suggestions like scroll, do x, ... to get the solution right.

Task to validate: {{task}}.

Return a JSON object with 2 keys: `is_valid` and `reason`:
- `is_valid` is a boolean that indicates if the output is correct.
- `reason` is a string that explains why it is valid or not.

Example:
```json
{{&example}}
```

Your turn:
"""


class CompletionValidation(BaseModel):
    is_valid: bool
    reason: str


@final
class CompletionValidator:
    def __init__(
        self,
        llm: LLMEngine,
        perception: BasePerception,
        use_vision: bool = True,
        include_attributes: bool = True,
        max_steps: int = 3,
    ):
        self.use_vision = use_vision
        self.include_attributes = include_attributes
        self.llm: LLMEngine = llm
        self.conv: Conversation = Conversation()
        self.perception: BasePerception = perception
        self.max_actions: int = max_steps

    @staticmethod
    def example() -> CompletionValidation:
        return CompletionValidation(
            is_valid=False,
            reason="The user wanted to search for 'cat photos', but the agent searched for 'dog photos' instead.",
        )

    def validation_message(
        self, output: CompletionAction, history: TrajectoryHistory[BaseModel], last_obs: Observation
    ) -> str:
        previous_results = [result for step in history.steps for result in step.results][-self.max_actions :]

        return f"""
Last observation:
{self.perception.perceive(last_obs)}


Last action executions:
{"/n".join(TrajectoryHistory.perceive_execution_result(result) for result in previous_results)}

Agent task output:
{output}
"""

    async def validate(
        self, task: str, output: CompletionAction, history: TrajectoryHistory[BaseModel]
    ) -> CompletionValidation:
        """Validate the output of the last action is what the user wanted"""
        last_obs = history.observations()[-1]

        self.conv.reset()
        system_prompt = chevron.render(system_rules, {"task": task, "example": self.example().model_dump_json()})
        self.conv.add_system_message(content=system_prompt)

        validation_message = self.validation_message(output, history, last_obs)

        self.conv.add_user_message(
            content=validation_message,
            image=(last_obs.screenshot if self.use_vision else None),
        )

        answer: CompletionValidation = await self.llm.structured_completion(self.conv.messages(), CompletionValidation)
        return answer
