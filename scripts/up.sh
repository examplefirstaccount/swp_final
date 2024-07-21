# shellcheck disable=SC2148

if ! [[ -f .venv/bin/pybabel ]]; then
    poetry install --with dev
fi

./scripts/locales.sh

docker compose up -d --build