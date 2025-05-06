import typer
from entrypoints.cli.commands import (
    add_admin,
    add_members,
    list_members,
    login_admins,
    add_book,
    list_books,
    member,
)

app = typer.Typer()

app.command()(add_admin.add_admin)
app.command()(login_admins.login_admin)
app.command()(add_book.add_book)
# app.command()(list_members.list_members)
app.command()(list_books.view_books)
app.command()(list_members.view_members)
app.command()(add_members.add_member)


if __name__ == "__main__":
    app()
