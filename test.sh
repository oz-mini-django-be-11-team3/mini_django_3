set -eo pipefail

COLOR_GREEN=$(tput setaf 2)
COLOR_NC=$(tput sgr0) # No Color

echo "Starting black"
uv run black .
echo "OK"

echo "Starting isort"
uv run isort .
echo "OK"

echo "${COLOR_GREEN}ALL tests passed successfully!${COLOR_NC}"