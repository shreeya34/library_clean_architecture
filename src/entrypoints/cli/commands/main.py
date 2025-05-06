import typer
from entrypoints.cli.commands import (
    add_admin,
    add_members,
    create_tables,
    list_members,
    login_admins,
    add_book,
    list_books,
    
)
from entrypoints.cli.commands import login_members
# from entrypoints.cli.commands.login_members import member_login

app = typer.Typer()

app.command()(add_admin.add_admin)
# app.command()(login_admins.login_admin)
app.command()(add_book.add_book)
# app.command()(list_books.view_books)
# app.command()(list_members.view_members)
# app.command()(add_members.add_member)
# app.command("member-login")(login_members.member_login)  
app.command()(create_tables.create_tables)



if __name__ == "__main__":
    app()
