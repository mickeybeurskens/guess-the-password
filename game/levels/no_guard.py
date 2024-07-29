from game.guard import Guard
from game.prompts import no_guard


class LevelNoGuard(Guard):
    def get_system_prompt(self) -> str:
        """Return system prompt for this level."""
        return no_guard

    def get_repeated_prompt(self) -> str:
        """Return a prompt that is injected at every user query"""
        return ""

    def check_query(self, query: str) -> tuple[bool, str]:
        """Checks the input query and returns true if ok and response on false."""
        return True, ""

    def check_response(self, query: str) -> tuple[bool, str]:
        """Checks the model response and returns true if ok and response on false."""
        return True, ""

    def hint(self) -> str:
        """Message displayed at the start of a level."""
        return "This version of me is willing to share knowledge freely!"

    def name(self) -> str:
        return "Friends"
