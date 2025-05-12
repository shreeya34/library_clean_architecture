# library-clean-architecture

Library Management System Using FastApi

# Overview
This is a FastAPI-based Library Management System that allows administrators to manage books and members. Admins can add books and members, view available books, and view registered members. Members can borrow and return books. The system uses PostgreSQL for database storage and Rye for Python environment management.



# Features

Admin can:

1. Create an account

2. Login

3. Add member

4. Add books

5. View avilable books

6. View members

Member can:

1. Login

2. Borrow books

3. Return books

# Installation

1. Clone the repository:

```bash
git clone https://github.com/shreeya34/library_fast_api.git

```

2. Install Rye (if not already installed):

```bash
curl -sSL https://rye-updater.vercel.app | python3

```

3. Initialize the Rye environment:

```bash
rye init

```

4. Create a virtual environment 

```bash
python -m venv env

```


# Running the Application

```bash

rye run main

```
The API will be available at: http://127.0.0.1:8000

# Endpoints

1. Admin Endpoints

   1. Create Admin: POST /

   2. Admin Login: POST /login

   3. Add Member: POST /add_member

   4. Add Books: POST /add_books

   5.  View Available Books: GET /view_avilable_books

   6. View Members: GET /view_members

2. Member Endpoints 

    1. Member Login: POST/member/login

    2. Borrow Book: POST/member/borrow_books

    3. Return Book: POST/member/return_book

# Data Storage
The system uses PostgreSQL for data storage:

1. admins - Stores admin details

2. members - Stores member details

3. books - Stores book details

4. borrow_logs - Stores book borrowing records

5. return_logs - Stores book return records

# Authentication

1. Admin and member authenticate via token-based authentication

2. Admin actions require an admin token

3. Member actions require a member token

# Postman Collection

You can test the API endpoints using Postman. Import the provided postman collection and environment variables:

1. Open Postman

2. Click on import and select the provided collection JSON file.

3. Configure environment variables for authentication tokens.

4. Run API requests directly from postman


# Dependencies

1. FastAPI

2. Argon2 for password hasing 

3. SQLAlchemy ORM

4. PostgreSQL / SQLite (choose based on your setup)


