import typer
from sqlalchemy.orm import Session
from modules.infrastructure.database.postgres_manager import PostgresManager
from modules.domain.admin.models import NewMember
from modules.infrastructure.services.admin_services import get_member as core_get_member, view_all_members as core_view_all_members, view_member_by_id as core_view_member_by_id

postgres_manager = PostgresManager()
db: Session = next(postgres_manager.get_db())

def add_member(name: str = typer.Option(..., help="Member name"),
               role: str = typer.Option(..., help="Member role")):
    new_member = NewMember(name=name, role=role)
    response = core_get_member(new_member, db)
    typer.echo(f"New member '{name}' added successfully with role '{role}'.")

def view_members():
    response = core_view_all_members(db)
    for member in response["filtered_members"]:
        typer.echo(f"Name: {member['name']}, Role: {member['role']}, Member ID: {member['member_id']}")

def view_member(member_id: str = typer.Option(..., help="Member ID")):
    response = core_view_member_by_id(member_id, db)
    typer.echo(f"Name: {response['name']}, Role: {response['role']}, Member ID: {response['member_id']}")

if __name__ == "__main__":
    typer.run(add_member)
