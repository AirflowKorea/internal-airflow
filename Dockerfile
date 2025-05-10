FROM astrocrpublic.azurecr.io/runtime:3.0-1

USER root
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

USER astro