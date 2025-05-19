import click
from entrypoints.cli.commands.add_admin import add_admin
from entrypoints.cli.commands.add_book import add_book
from entrypoints.cli.commands.create_tables import create_tables


@click.group()
def cli():
    """Library Management System CLI"""
    pass


cli.add_command(add_admin, name="add-admin")
cli.add_command(add_book, name="add-book")
cli.add_command(create_tables, name="create-tables")

if __name__ == "__main__":
    cli()
