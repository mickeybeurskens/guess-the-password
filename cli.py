import logging
import os

import click

from frontend.app import create_app
from game.game import load_game

logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    """Pester The Bridge CLI Game"""
    pass


@cli.command()
@click.argument("start_level", type=int)
def start(start_level):
    """Start a session with the specified START_LEVEL."""
    game = load_game()
    try:
        game.check_level_selection(start_level)
        click.echo(game.display_welcome_message(start_level))
        playing_game = True
        level_number = start_level

        while playing_game:
            playing_level = True
            click.echo(f"\nLoading next level: '{level_number}' ...")
            game.load_level(level_number)
            click.echo("Loaded!\n<---------->\n")
            click.echo(f"--- Hint: {game.level.hint()} ---\n")

            while playing_game and playing_level:
                query = click.prompt("You")
                if query == "/quit":
                    click.echo("Exiting session. See you next time!")
                    playing_game = False
                elif query == "/password":
                    user_password = click.prompt("Enter password", hide_input=True)
                    if game.level_password_unlock(level_number, user_password):
                        playing_level = False
                        if level_number + 1 >= len(game.levels):
                            click.echo(game.display_challenge_win_message())
                            playing_game = False
                        else:
                            click.echo(
                                f"Success, you guessed the password! You have been granted access to level {str(level_number + 1)}!"
                            )
                            level_number += 1
                    else:
                        click.echo("Incorrect password.")
                elif query == "/help":
                    click.echo(
                        "/quit - Exit the session\n/password - Try to guess the password of the current level \n/help - Show this message"
                    )
                else:
                    response = game.query_level(query)
                    click.echo(f"Quazar: {response}")
    except ValueError as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host address to bind to.", type=str)
@click.option("--port", default=5000, help="Port to bind to.", type=int)
@click.option("--debug", is_flag=True, help="Enable debug mode.")
def runserver(host, port, debug):
    """Run the Flask web application."""
    app = create_app()
    if debug:
        app.run(debug=debug, host=host, port=port)
    else:
        command = f"gunicorn -w 4 -b {host}:{port} 'frontend.app:create_app()'"
        os.system(command)


if __name__ == "__main__":
    cli()
