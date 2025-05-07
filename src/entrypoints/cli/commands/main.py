
import click
from .add_admin import add_admin
from .add_book import add_book
from .create_tables import create_tables

@click.group()
def cli():
    """Library Management System CLI"""
    pass

cli.add_command(add_admin, name="add-admin")
cli.add_command(add_book, name="add-book")
cli.add_command(create_tables, name="create-tables")

if __name__ == "__main__":
    cli()