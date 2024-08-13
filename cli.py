import logging
import os

import click

from frontend.app import create_app

logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    """Command line tool for Pass The Bridge."""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host address to bind to.", type=str)
@click.option("--port", default=5000, help="Port to bind to.", type=int)
@click.option("--debug", is_flag=True, help="Enable debug mode.")
@click.option(
    "--model-type",
    default="ollama",
    type=click.Choice(["ollama", "chatgpt", "claude"], case_sensitive=False),
    help="Select the model to use (ollama, chatgpt, claude).",
)
def runserver(host, port, debug, model_type):

    """Run the Flask web application."""
    os.environ["GTP_MODEL_TYPE"] = model_type  #FIXME: Set so "create_app" can be called with gunicorn
    if debug:
        app = create_app()
        app.run(debug=debug, host=host, port=port)
    else:
        command = f"gunicorn -w 4 -b {host}:{port} 'frontend.app:create_app()'"
        os.system(command)

if __name__ == "__main__":
    cli()
