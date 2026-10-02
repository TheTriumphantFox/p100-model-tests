#!/usr/bin/env bash
# Run a command inside the aider-benchmark container with this run's mounts.
# Host networking so the container reaches the llama.cpp router on 127.0.0.1:8081.
T=/home/hm/Projects/Tests
R=${R:-$T/2026-10-01/aider-polyglot-10h}
exec podman run --rm --network host --memory=12g --memory-swap=12g -e AIDER_DOCKER=1 \
  -e OPENAI_API_BASE=http://127.0.0.1:8081/v1 -e OPENAI_API_KEY=sk-local \
  -v $T/tools/aider:/aider:ro -v $T/tools/polyglot-benchmark:/polyglot:ro \
  -v $R:/run -v $T/scripts:/scripts:ro \
  -v $T/tools/polyglot-cache/gradle:/root/.gradle \
  -v $T/tools/polyglot-cache/cargo-registry:/root/.cargo/registry \
  ${CTR_NAME:+--name $CTR_NAME} \
  localhost/aider-benchmark "$@"
