from typer import Typer
from rich.panel import Panel
from typing_extensions import Annotated

app = Typer(name="aide")


@app.command()
def main(prompt: Annotated[str, "prompt"] = None):
    print(f"Hello {prompt}")


if __name__ == "__main__":
    app()
