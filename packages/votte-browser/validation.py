from collections.abc import Sequence

from loguru import logger
from notte_core.actions import InteractionAction

from notte_browser.tagging.type import PossibleAction


class ActionListValidationPipe:
    @staticmethod
    def forward(
        inodes_ids: list[str],
        actions: Sequence[PossibleAction],
        # Just for logging purposes
        previous_action_list: Sequence[InteractionAction] | None = None,
        verbose: bool = False,
    ) -> Sequence[PossibleAction]:
        # this function returns a list of valid actions (appearing in the context)
        actions_ids = {action.id for action in actions}
        previous_action_ids = {action.id for action in (previous_action_list or [])}
        hallucinated_ids = {id for id in actions_ids if id not in inodes_ids}
        missed_ids = {id for id in inodes_ids if (id not in actions_ids) and (id not in previous_action_ids)}

        if len(hallucinated_ids) > 0 and verbose:
            logger.debug(f"Hallucinated actions: {len(hallucinated_ids)} : {hallucinated_ids}")
            # TODO: log them into DB.

        if len(missed_ids) > 0 and verbose:
            logger.debug(f"Missed actions: {len(missed_ids)} : {missed_ids}")
            # TODO: log them into DB.

        return [a for a in actions if a.id not in missed_ids and a.id not in hallucinated_ids]
