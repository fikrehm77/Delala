# Base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy Poetry installation script
RUN apt update && apt install -y curl
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the Poetry files and install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

# Copy the bot files
COPY . .

# Run the bot
CMD ["poetry", "run", "python", "main.py"]
