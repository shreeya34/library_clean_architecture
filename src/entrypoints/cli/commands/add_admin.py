import click
from entrypoints.cli.db_utils import get_db
from modules.application.use_cases.admin.create_admin import CreateAdminUseCase
from modules.infrastructure.repositories.admin.admin_repositories_impl import (
    AdminRepository,
)
from entrypoints.api.admin.request import CreateModel
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
        create_admin_usecase = CreateAdminUseCase(admin_repo)

        result = create_admin_usecase.register_admin(
            db=db,
            admin=CreateModel(username=username, password=password)
        )

        click.secho(f"Admin '{result['username']}' created successfully!", fg="green")

    except Exception as e:
        click.secho(f"Unexpected Error: {e}", fg="red")
