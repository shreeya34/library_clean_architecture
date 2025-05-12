import click
from entrypoints.cli.db_utils import get_db
from modules.infrastructure.repositories.admin.admin_repositories_impl import (
    AdminRepository,
)
from modules.interfaces.request.admin_request import CreateModel
from modules.application.services.admin_services import AdminService


@click.command()
@click.option("--username", required=True, prompt="Admin username")
@click.option(
    "--password", required=True, prompt=True, hide_input=True, confirmation_prompt=True
)
def add_admin(username, password):
    """Create a new admin account"""
    db = get_db()
    try:
        admin_repo = AdminRepository()
        admin_service = AdminService(admin_repo)

        admin_service.create_admin(
            CreateModel(username=username, password=password), db
        )
        click.secho(f"Admin '{username}' created successfully!", fg="green")

    except Exception as e:
        click.secho(f"Unexpected Error: {e}", fg="red")
