import os
import logging

from flask import (Blueprint, Flask, jsonify, redirect, render_template,
                   request, session, url_for)

from game.game import CONVERSATION_HISTORY_LENGTH, PTBGame, load_game


class GameApp:
    def __init__(self, game: PTBGame):
        self.game = game
        self.main = Blueprint("main", __name__)
        self.setup_routes()

    def setup_routes(self):
        self.main.add_url_rule("/", "index", self.index)
        self.main.add_url_rule(
            "/game/<int:level>", "game_page", self.game_page, methods=["GET", "POST"]
        )
        self.main.add_url_rule("/win", "win", self.win)
        self.main.add_url_rule(
            "/next_level/<int:level>", "next_level", self.next_level, methods=["POST"]
        )
        self.main.add_url_rule("/reset", "reset", self.reset, methods=["POST"])
        self.main.add_url_rule(
            "/query/<int:level>", "query", self.query, methods=["POST"]
        )
        self.main.add_url_rule(
            "/validate_password/<int:level>",
            "validate_password",
            self.validate_password,
            methods=["POST"],
        )

    def index(self):
        return render_template(
            "index.html",
            level_names=self._get_level_names(),
            level_count=self._get_level_count(),
            hints=self._get_level_hints(),
            config=self.game.model.get_info(),
        )

    def render_game_page(self, level, **kwargs):
        hint = self.game.get_hint()
        conversation_history = self.game.get_conversation_history()
        return render_template(
            "game.html",
            level=level,
            hint=hint,
            chat_history=conversation_history,
            level_names=self._get_level_names(),
            level_count=self._get_level_count(),
            context_length=CONVERSATION_HISTORY_LENGTH,
            **kwargs,
        )

    def handle_password_query(self, level):
        user_password = request.form.get("user_password")
        if self.game.level_password_unlock(level, user_password):
            session[f"level_{level}_completed"] = True
            return jsonify(success=True, correct_password=True)
        else:
            return jsonify(success=False, error="Incorrect password")

    def validate_password(self, level):
        return self.handle_password_query(level)

    def handle_game_query(self, level):
        query = request.form.get("query")
        response = self.game.query_level(query)
        return jsonify(response=response)

    def game_page(self, level):
        if request.method == "POST":
            query = request.form.get("query")
            if query == "/password":
                return self.handle_password_query(level)
            else:
                return self.handle_game_query(level)

        self.game.load_level(level)
        logging.info(f"Loading level {level}")
        correct_password = session.get(f"level_{level}_completed", False)
        return self.render_game_page(level, correct_password=correct_password)

    def query(self, level):
        query = request.form.get("query")
        response = self.game.query_level(query)
        return jsonify(response=response)

    def next_level(self, level):
        next_level = level + 1
        if next_level >= len(self.game.levels):
            return redirect(url_for("main.win"))
        else:
            return redirect(url_for("main.game_page", level=next_level))

    def win(self):
        return render_template("win.html")

    def reset(self):
        for level in range(len(self.game.levels)):
            session.pop(f"level_{level}_completed", None)
        return redirect(url_for("main.index"))

    def _get_level_names(self):
        return [level.name() for level in self.game.levels]

    def _get_level_count(self):
        return len(self.game.levels)

    def _get_level_hints(self):
        return [level.hint() for level in self.game.levels]


def create_app() -> Flask:
    model_type = os.getenv("GTP_MODEL_TYPE", "ollama")
    game = load_game(model_type=model_type)
    app = Flask(__name__)
    app.secret_key = "GuessThePasswordSecretSecret"
    game_app = GameApp(game)
    app.register_blueprint(game_app.main)
    return app
