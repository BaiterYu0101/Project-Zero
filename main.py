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
    push: bool = typer.Option(
        False,
        "--push",
        help="If set, ask whether to commit and push generated files to git.",
    ),
):
    clean_name = name.lower().replace(" ", "-").replace("_", "-")

    print(f"[bold blue]   Scaffolding project:[/bold blue] [green]{name}[/green]")

    project_path = Path(clean_name)
    project_path.mkdir(exist_ok=True)

    templates = {
        "deployment.yaml.j2": "deployment.yaml",
        "services.yaml.j2": "service.yaml",
    }

    for t_name, f_name in templates.items():
        template = env.get_template(t_name)
        output = template.render(
            app_name=clean_name,
            app_port=port,
            replica_count=replicas,
            service_type=service_type,
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


if __name__ == "__main__":
    app()