import json
import logging
from abc import ABC, abstractmethod

import requests
from pydantic import BaseModel


class ModelInterface(ABC):
    """Defines interface to communicate with LLM models."""

    @abstractmethod
    def query(self, query: str) -> str:
        """Query model and return response."""

    @abstractmethod
    def get_info(self) -> str:
        """JSON with model info"""


class OllamaInterfaceConfig(BaseModel):
    host: str = "http://localhost"
    port: int = 443
    subdomain: str = "/api"
    model: str = "llama3:latest"


class OllamaInterface(ModelInterface):
    def __init__(self, config: OllamaInterfaceConfig):
        self.config = config
        self._model_params = {"model": self.config.model}
        self._url = f"{self.config.host}:{self.config.port}{self.config.subdomain}"
        self._check_available_models()

    def query(self, query: str) -> str:
        """Query a ollama model and get a response."""
        logging.info(f"Query: {query}")
        payload = {**self._model_params, "prompt": query}
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            self._url + "/generate", data=json.dumps(payload), headers=headers
        )

        if response.status_code != 200:
            raise Exception(
                f"Request failed with status code {response.status_code}: {response.text}"
            )

        return self._parse_response(response)

    def get_info(self) -> dict:
        return self.config.model_dump()

    def _check_available_models(self):
        """Send a request to the API endpoint that returns all available models."""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{self._url}/tags", headers=headers)

        if response.status_code != 200:
            logging.warning(
                f"Failed to fetch available models with status code {response.status_code}: {response.text}"
            )
            return

        available_models = [model["name"] for model in response.json()["models"]]

        if self.config.model not in available_models:
            logging.warning(
                f"Model '{self.config.model}' is not available on the server. Available models are: {', '.join(available_models)}"
            )

    def _parse_response(self, response) -> str:
        partial_responses = [json.loads(r) for r in response.text.splitlines()]
        full_response = ""
        for r in partial_responses:
            full_response += r["response"]
            if r["done"]:
                break
        logging.info(f"Response: {full_response}")
        return full_response
