#!/bin/bash

/bin/ollama serve &
pid=$!

sleep 5

model=$(grep '"model"' /root/config/ollama.json | sed 's/.*"model": "\(.*\)".*/\1/' | tr -d '", ')

echo "Retrieve $model model..."
ollama pull "$model"
echo "Done!"

wait $pid
