FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y rsync procps && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the package in editable mode
# This allows us to modify code if we mount volumes and see changes immediately if we were to rerun main
# We still run this here to cache dependencies if we had them
# Install the package in editable mode
# This allows us to modify code if we mount volumes and see changes immediately if we were to rerun main
# We still run this here to cache dependencies if we had them
RUN pip install -e .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
CMD ["pusher"]
