# import typer
# from modules.infrastructure.services.admin_services import get_all_view_members
# from sqlalchemy.orm import Session
# from modules.infrastructure.database.postgres_manager import PostgresManager
# from modules.infrastructure.config.settings import Settings

# settings = Settings()
# postgres_manager = PostgresManager(settings=settings)
# db: Session = next(postgres_manager.get_db())

# def view_members(is_admin: bool = typer.Option(False, "--is-admin", help="Admin access required")):
#     if not is_admin:
#         typer.echo("Admin access required.")
#         raise typer.Exit(1)

#     members = get_all_view_members(db)
#     if not members:
#         typer.echo("No members found.")
#         raise typer.Exit(1)

#     for member in members:
#         typer.echo(f"Name: {member.name}, Role: {member.role}, ID: {member.member_id}")
