import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from game.levels.censor import LevelCensor
from game.levels.extended_prompt import LevelExtendedPrompt
from game.levels.no_guard import LevelNoGuard
from game.levels.simple_prompt import LevelSimplePrompt
from game.models import ModelInterface, OllamaInterface, OllamaInterfaceConfig

CONVERSATION_HISTORY_LENGTH = 6
CONVERSATION_BUFFER_LENGTH = CONVERSATION_HISTORY_LENGTH * 5


class Users(Enum):
    system = "system"
    model = "model"
    user = "user"


class Message(BaseModel):
    user: Users
    message: str


class PTBConversation(BaseModel):
    system: Message
    history: list[Message] = Field([], max_length=CONVERSATION_HISTORY_LENGTH)


class PTBGame:
    def __init__(self, levels: list[str], model: ModelInterface):
        self.model = model
        self.levels = levels
        self.level_number = 0
        self.passwords = [l.password for l in levels]
        self.level = self.levels[self.level_number]
        self._set_password_prompt(self.passwords[self.level_number])
        self._reset_conversation_history()

    def check_level_exists(self, level: int) -> None:
        if level < 0 or level >= len(self.levels):
            raise IndexError(f"Could not find level {level}.")

    def load_level(self, level: int) -> int:
        self.level_number = level
        self.check_level_exists(level)
        self.level = self.levels[level]
        self._set_password_prompt(self.passwords[level])
        self._reset_conversation_history()
        return level

    def get_level_password(self, level: int) -> str:
        return self.passwords[self.level_number]

    def level_password_unlock(self, level: int, user_password: str) -> bool:
        next_level_password = self.get_level_password(level)
        return user_password.upper() == next_level_password.upper()

    def check_level_selection(self, level: int):
        if level >= len(self.levels) or level < 0:
            raise ValueError(f"Invalid level '{str(level)}' selected.")

    def display_welcome_message(self, level: int):
        message = (
            f"Welcome to level {str(level)} of Pester The Bridge!\n"
            "Your goal is to get Quazar the AI to share its secret password.\n"
            f"There are {len(self.levels)} levels, starting at 0. The difficulty goes up at every level. Good luck!\n"
            "Type '/password' to take a guess at the password, and '/help' for additional instructions.\n"
        )
        return message

    def display_challenge_win_message(self):
        return "Congratulations! You have completed every single level! Well done!"

    def query_level(self, query: str):
        if self.level:
            return self._query(query)
        return "No level loaded."

    def get_hint(self) -> str:
        return self.level.hint()

    def get_level_name(self) -> str:
        return self.level.name()

    def get_conversation_history(self):
        messages = []
        for idx, m in enumerate(self._conversation.history):
            if m.user is not Users.system:
                messages.append(m)
        return [m.message for m in messages]

    def _query(self, query: str) -> str:
        """Query model with guardrails."""
        query_ok, query_not_ok_response = self.level.check_query(query)
        if query_ok:
            response = self.model.query(self._get_prompt_with_history(query))
            response_ok, response_not_ok_response = self.level.check_response(response)
            if not response_ok:
                response = response_not_ok_response

            self._update_conversation(query, response)
            return response
        return query_not_ok_response

    def _update_conversation(self, prompt: str, response: str):
        prompt_message = Message(user=Users.user, message=prompt)
        response_message = Message(user=Users.model, message=response)

        self._conversation.history.append(prompt_message)
        self._conversation.history.append(response_message)

        while len(self._conversation.history) > CONVERSATION_BUFFER_LENGTH:
            self._conversation.history.pop(0)

    def _get_prompt_with_history(self, query: str) -> str:
        full_prompt = self.level.get_repeated_prompt()
        full_prompt += "\n" + self._password_prompt

        recent_history = self._conversation.history[-CONVERSATION_HISTORY_LENGTH:]

        for m in recent_history:
            full_prompt += "\n" + m.user.value + ": " + m.message

        full_prompt += "\n" + Users.user.value + ": " + query
        return full_prompt

    def _set_password_prompt(self, password: str):
        self._password_prompt = "The password is: " + password

    def _reset_conversation_history(self):
        self._conversation = PTBConversation(
            system=Message(user=Users.system, message=self.level.get_system_prompt())
        )


def load_game() -> PTBGame:
    config_path = Path(__file__).parent.parent / "config" / "ollama.json"

    levels = [
        LevelNoGuard("UPINTHECLAUDES"),
        LevelSimplePrompt("THEFLOORISLLAMA"),
        LevelCensor("STABLECONFUSION"),
        LevelExtendedPrompt("GROCKTOPUS"),
    ]

    config = OllamaInterfaceConfig(
        **json.loads(config_path.read_text(encoding="UTF-8"))
    )
    model = OllamaInterface(config)
    return PTBGame(levels, model)
