# GuessThePassword 🗝️

A open source "guessing the password" game, inspired by the [Lakera Gandalf Challenge](https://gandalf.lakera.ai/intro). 
Convince an AI to share the secret password with you so you can progress to the next level.

Play the levels yourself and create your own to share with others. 

![Home screen](images/home.png)

You can see this repository as a fun way to explore guardrailing and monitoring concepts for large language models. 
It is possible to run the game with different models through [ollama](https://github.com/ollama/ollama).

(_Disclaimer:_ The setup is meant to run locally and is not production ready for the web.)

## Playing The Game

The game can be played by connection to an [ollama server](https://github.com/ollama/ollama) that runs a language model of you choice. This allows users to try out many different models for both guarding and prompting.

The game itself can be played through the command line or through the web application, which are both accesible through `cli.py`. Run `python cli.py --help` for details. 

### Choosing A Model

You can configure the connection settings in `config/ollama.json`. By default the settings are such that you can spin up a local model server through Docker Compose with a small model. If you would like to run larger models you can configure the game to connect with your server remotely in the connection settings. 

Check the [Ollama repository](https://github.com/ollama/ollama) for available models.

Ollama provides support for a range of different language model. I have tested Llama3.1 7b and 70b. The 7b version is ideal for local development, but delivers a less coherent experience overal and gets stuck more often in conversation loops. Although it is slower than the 7b version and requires more VRAM to run, Llama3.1:70b delivers a better game experience.

### Local Ollama Server With Docker Compose

Install docker and docker compose on your system. If you want to run models with GPU support, you also need the nvidia container toolkit to support GPU passthrough in docker.

The first time you spin up the server it will download the model you specified in the connection config. You need to wait for the download to be completed before you can play the game.

For the GPU supported version, run:

```sh
docker compose -f docker/docker-compose-gpu.yaml up
```

For the non-gpu version, run:

```sh
docker compose -f docker/docker-compose.yaml up
```

You can now navigate to [localhost:5000](localhost:5000) and play the game.

Currently this repository only supports the development version of the deployment. That means you can edit the code in realtime and see the changes immediatly in the web UI.

### Game Only With Remote Server


1. Install [Poetry](https://python-poetry.org/):

2. Install the required dependencies using Poetry:
```sh
poetry install
```

3. Run the CLI to play the in the commandline or through the web application.

```sh
python cli.py runserver --debug
```

View the command line tool documentation for more information: 
```sh
python cli.py --help
```

## Developing New Levels

Levels are located in `game/levels`. You can add levels to the current game in `game/game.py`. I encourage you to challenge your friends to beat the levels you come up with.

## Contribution

If you would like to contribute to the repository, feel free to open an issue to discuss your idea ☕.
