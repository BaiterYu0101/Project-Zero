# Project-Zero
**Project Zero** is a lightweight DevOps automation tool designed to bridge the gap between the local development and Kubernetes orchestration. It's built by using Python and Typer which helps in standardize the "Inner loop" of the deployment: Scaffolding, Building, Running and Deploying.

# Project Structure
```text
project_zero/
|---template
|    |--- deployment.yaml.j2
|    |--- services.yaml.j2
|    |--- Dockerfile.j2
|
|---main.py
|---'other are just test-app'
|--- etc
```

# Prerequisites
Before running the tools, make sure your laptop/computer has the followed installed:
- Python 3.9+
- Orbstack (or Docker Desktop) with Kubernetes enabled
- kubectl (installed via Homebrew/Orbstack)


# Installation

1. Install dependencies
``` bash 
pip install typer jinja2 rich
```
2. Setup the Global Alias (Recommended):
To run the tool from any folder using the ```pz``` command, add this to your ```~.zshrc```:
```bash
# Replace /path/to/project-zero with your actual folder path
alias pz = 'python3 /path/to/project-zero/main.py'
```

# Usage and Command
| Common | Description |
| :---   | :---        |
| pz doctor | Verifies your system has Git, Docker and Kubectl installed
| pz create | Interactive prompt to scaffold a new project with K8s manifests
| pz build | Builds a Docker image using the local Dockerfile
| pz run | Launches the container locally in detached nodes
| pz logs | Streams real-time logs from the running container
| pz deploy | Pushes the project manifests to the Kubernetes cluster
| pz scale | Instantly scales the number of running K8s pods
| pz delete | Cleans up all Docker and Kubernetes resources for a project
