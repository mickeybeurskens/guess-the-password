import logging
import os

import click

from frontend.app import create_app
from game.game import load_game

logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    """Command line tool for Pass The Bridge."""
    pass

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
