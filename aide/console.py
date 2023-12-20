import curses
from aide.editor import TextEditor
from typer import Typer, Option
from typing_extensions import Annotated

app = Typer(name="aide")


@app.command()
def main(
    text: Annotated[
        str, Option(help="The initial text that would be inserted into the editor")
    ] = None,
    model: Annotated[str, Option(help="The model to use for the AI")] = "mistral:text",
    ahead: Annotated[int, Option(help="Count of the words to predict")] = 5,
):
    text_editor = TextEditor(model=model, text=text, ahead=ahead)
    curses.wrapper(text_editor.run)


if __name__ == "__main__":
    app()
