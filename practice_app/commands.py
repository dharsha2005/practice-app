import click


@click.command("hello-app")
def hello():
    print("Hello from the custom Bench CLI!")


commands = [hello]