import typer

app = typer.Typer()

if __name__ == "__main__":
    command = typer.main.get_command(app)

    try:
        result = command(standalone_mode=False)
    except Exception as exception:
        raise exception

    sys.exit(0)
