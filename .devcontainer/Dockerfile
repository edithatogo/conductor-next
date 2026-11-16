FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm@sha256:10717c456fb0ac3a9a78c7d9d405599b589d8faf59865f7596a4b26995b7b14c

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && 
    apt-get install -y nodejs

# Install Mamba (via Micromamba)
RUN curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba && 
    mv bin/micromamba /usr/local/bin/micromamba && 
    micromamba shell init -s bash -p /opt/conda && 
    /usr/local/bin/micromamba install -y -n base -c conda-forge mamba

# Setup environment
COPY environment.yml /tmp/environment.yml
RUN mamba env update -n base -f /tmp/environment.yml && 
    rm /tmp/environment.yml

# Install VS Code extension development tools
RUN npm install -g @vscode/vsce typescript
