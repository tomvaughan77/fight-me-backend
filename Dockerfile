# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Add Poetry configuration variables
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/app"

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install Poetry
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
    && curl -sSL https://install.python-poetry.org | python3 -

# Copy only requirements to cache them in docker layer
WORKDIR $PYSETUP_PATH
COPY ./pyproject.toml ./poetry.lock ./

# Project initialization:
RUN poetry install --no-dev --no-root

# Copy all files
COPY . .

# Run the application:
CMD ["poetry", "run", "python", "fight_me_backend/main.py"]
