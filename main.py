# Makes the script work like a real terminal tool, like git
import subprocess
import typer
# The engine that fills in the blanks in the deployment.yaml.j2 template
from jinja2 import Environment, FileSystemLoader
# Helps create folders/files without making mistakes
from pathlib import Path
# Makes the terminal output look nice
from rich import print

app = typer.Typer() 
env = Environment(loader=FileSystemLoader("templates"))


def run_git_command(args: list[str], cwd: Path) -> bool:
    try:
        subprocess.run(args, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[bold red]Git error:[/bold red] {e}")
        return False


def is_git_repo(cwd: Path) -> bool:
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


@app.command()
def create(
    name: str = typer.Option(..., prompt="What is the project name?"),
    port: int = typer.Option(8000, prompt="What port does your app run on?"),
    replicas: int = typer.Option(3, prompt="How many replicas do you want?"),
    service_type: str = typer.Option(
        "ClusterIP",
        prompt="What type of service do you want? (ClusterIP, NodePort, LoadBalancer)",
    ),
    size: str = typer.Option(None),  # No default or prompt here, allow the user to reprompt again if type wrongly
    push: bool = typer.Option(
        False,
        "--push",
        help="If set, ask whether to commit and push generated files to git.",
    ),
):
    resources = {
        "Small": {"cpu": "250m", "memory": "256Mi"},
        "Medium": {"cpu": "500m", "memory": "512Mi"},
        "Large": {"cpu": "1000m", "memory": "1Gi"}
    }

    #Loop this again to have a better prompt
    while size not in resources:
        #Means if User provided but invalid prompt, it will comes to this if....
        if size is not None:
            print(f"[bold red]Invalid size '{size}'. Please choose Small, Medium or Large. [/bold red]")
        size = typer.prompt("App size? (Small/Medium/Large)", default="Small")
        #Means if User provide the size 
        if size not in resources:
            continue
    clean_name = name.lower().replace(" ", "-").replace("_", "-")

    print(f"[bold blue]   Scaffolding project:[/bold blue] [green]{name}[/green]")

    project_path = Path(clean_name)
    project_path.mkdir(exist_ok=True)

    templates = {
        "deployment.yaml.j2": "deployment.yaml",
        "services.yaml.j2": "service.yaml",
        "Dockerfile.j2": "Dockerfile",
        "README.md": "README.md"
    }

    for t_name, f_name in templates.items():
        template = env.get_template(t_name)
        output = template.render(
            app_name=clean_name,
            app_port=port,
            replica_count=replicas,
            service_type=service_type,
            limits=resources[size],
        )
        with open(project_path / f_name, "w") as f:
            f.write(output)
            print(f" [dim]Created {f_name}[/dim]")

    print(f"[bold green] Success![/bold green] Files generated in [yellow]./{clean_name}[/yellow]")

    if push:
        if not typer.confirm("Do you want to commit and push these files to git now?"):
            print("[yellow]Push canceled. No git commands were run.[/yellow]")
            raise typer.Exit()

        repo_root = Path.cwd()
        if not is_git_repo(repo_root):
            print("[bold red]No git repository found in the current folder.[/bold red]")
            print("Initialize a repo first with `git init` or run this command from an existing repo.")
            raise typer.Exit(code=1)

        print("[bold blue]Staging files...[/bold blue]")
        if not run_git_command(["git", "add", str(project_path)], cwd=repo_root):
            raise typer.Exit(code=1)

        print("[bold blue]Committing files...[/bold blue]")
        if not run_git_command(
            ["git", "commit", "-m", f"Add {clean_name} project files"], cwd=repo_root
        ):
            raise typer.Exit(code=1)

        if typer.confirm("Do you want to push this commit to the remote repository now?"):
            print("[bold blue]Pushing to remote...[/bold blue]")
            if not run_git_command(["git", "push", "origin", "main"], cwd=repo_root):
                raise typer.Exit(code=1)
            print("[bold green]Push complete![/bold green]")
        else:
            print("[yellow]Push skipped. Commit is ready locally.[/yellow]")

@app.command()
def doctor():
    "Verify that Jerry's M5 MacBook is ready for DevOps work."
    tools = ["git", "docker", "kubectl", "python3"]
    print(f"[bold blue] Running System Diagnostics...[/bold blue]")

    for tool in tools:
        try:
            # 'which' finds where a program is installed
            result = subprocess.run(["which", tool], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  [green]✅ {tool}[/green] is installed at: [dim]{result.stdout.strip()}[/dim]")
            else:
                print(f"  [red]❌ {tool}[/red] is NOT found!")
        except Exception:
            print(f"  [red]❌ Error checking for {tool}[/red]")

    print("\n[bold green]System Check Complete![/bold green]")

@app.command()
def build (project_name: str):

    #Standardize the naming of the project 
    clean_name = project_name.lower().replace(" ", "-").replace("_", "-")
    project_path = Path(clean_name)

    #Check is the project folder exist??
    if not project_path.exists():
        print(f"[bold red]Error:[/bold red] Folder [yellow]'{clean_name}'[/yellow] has not been found!")
        raise typer.Exit(code=1) #Code=1, means "exit with an error status"
    
    #Check is there a docker file??
    if not(project_path / "Dockerfile").exists():
        print(f"[bold red]Error:[/bold red]No Docker file in [yellow]'{clean_name}'")
        print("RUn the 'create' command first!")
        raise typer.Exit(code=1) #Code=1, prompt to out the loop with an error status
    print(f"[bold blue] Building the Docker image: [/bold blue][green]:latest[/green]")

    try: 
        subprocess.run(
            ["docker", "build", "-t", f"{clean_name}:latest", "."], #Means use the list of word here...if not, the python will think that they are having the same multiple proejct if having the name of my app, actually is my-app...
            cwd=project_path,
            check=True
        )
        print(f"\n[bold green]Success![/bold green] Image[yellow]{clean_name}:latest[/yellow] is ready.")
        print(f"[dim]Run 'docker image'to see it on your Mac.[/dim]" )

    except subprocess.CalledProcessError:
        print(f"\n[bold red]Build Failed...[/bold red] Ensure your Docker is running.")
    except Exception as e:
        print(f"[bold red]Unexpected Error[/bold red]")

@app.command()
def run(project_name: str, port: int = 8000):
   """
   Starts your Docker container so you can see it in your browser.
   Usage: python3 main.py run {project_name}
   """
   clean_name = project_name.lower().replace(" ","-").replace("_","-")

   print(f"[bold blue] Starting container:[/bold blue] [green] {project_name} [/green]")
   print(f"[dim]Access it at: http://localhost:{port}[/dim]")
#Remove any old container with the same name so there's no conflict
   try:
       subprocess.run(["docker", "rm", "-f", clean_name], capture_output=True)

#Step 2: Run the new container
#-d: Run in the background (detached)
#-p: Map the ports (Mac_Port: Container_Port)
#-name: Give it a clean name
       subprocess.run(
        [
            "docker", "run", "-d",
            "-p", f"{port}:{port}",
            "--name", clean_name,
            f"{clean_name}:latest"
        ],
        check=True
    )
       print(f"[bold green]Container is currently running!!![/bold green]")
   except subprocess.CalledProcessError:
       print(f"[bold red] Failed to start the container.[/bold red] DId you run 'build first?")

@app.command()
def logs(project_name: str):
    """Streams logs from your running container. Press Ctrl+C to stop."""
    clean_name = project_name.lower().replace(" ", "-").replace("_", "-")
    print(f"[bold blue] Streaming logs for:[/bold blue] [green]{clean_name}[/green]\n")

    try:
        subprocess.run(["docker", "logs", "-f", clean_name], check=True)
    except KeyboardInterrupt:
        print("\n[yellow]Stopped following logs.[/yellow]")
    except subprocess.CalledProcessError:
        print(f"[bold red]No logs found for {clean_name}.[/bold red]Is it running?")

@app.command()
def deploy(project_name: str):
    """
    Deploys your project to the local Kubernetes cluster.
    """
    clean_name = project_name.lower().replace(" ", "-").replace("_", "-")
    project_path = Path(clean_name)

    # 1. CHECK IF THE PROJECT FOLDER EXISTS
    if not project_path.exists():
        print(f"[bold red]Error:[/bold red] Project folder[yellow]'{clean_name}'[/yellow] not found.")
        raise typer.Exit(1)
    print(f"[bold blue] Deploying to Kubernetes:[/bold blue][green]{clean_name}[/green]")

    try:
        # 2. The 'apply' command:
        # '-f .' means "find all YAML files in this folder and apply them"
        subprocess.run(
            ["kubectl", "apply", "-f", "." ],
            cwd=project_path,
            check=True
        )
        print(f"\n[bold green]Deployment succesful![/bold green]")
        print(f"[dim]Check your OrbStack dashboard under 'Pods' to see it turn green![/dim]")
    except subprocess.CalledProcessError:
        print(f"\n[bold red]Deployment failed.[/bold red]Is Kubernetes enabled in Orbstack?")
    except Exception as e:
        print(f"[bold red]Unexpected Error[/bold red] {e}")


#For clearup
@app.command()
def delete(project_name: str):
    "Cleans up both Kubernetes and Docker resources for a project. "
    clean_name = project_name.lower().replace(" ", "-").replace("_","-")
    project_path = Path(clean_name)

    print(f"[bold red] Deleting resources for:[/bold red] [yellow]{clean_name}[/yellow]")
    
    #1. Clean up Kubernetes
    if project_path.exists():
        subprocess.run(["kubectl", "delete", "-f", "."], cwd=project_path)
    
    #2. Clean up Docker
    subprocess.run(["docker","rm", "-f", clean_name], capture_output=True)

    print(f"[bold green]System is clean![/bold green]")

#For AutoScale
@app.command()
def scale(project_name: str, replicas: int):
    "Changes the number of running pods instantly"
    clean_name = project_name.lower().replace(" ", "-").replace("_","-")
    print(f"[bold blue]Scaling{clean_name} to {replicas} replicas...[/bold blue]")

    try:
        subprocess.run([
            "kubectl", "scale", f"deployment/{clean_name}",
            f"--replicas={replicas}"
        ], check=True)
        print(f"[bold green]Scaling complete!![/bold green]")
    except subprocess.CalledProcessError:
        print(f"[bold red]Failed to scale. Is this project deployed?[/bold red]")
if __name__ == "__main__":
    app()