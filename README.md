# Kanmind API

Kanmind is a RESTful API for task and board management, built with **Django** and **Django REST Framework (DRF)**.  
It provides endpoints for **user authentication, boards, tasks, and comments**.

---

## Features

- **Authentication**
  - User registration and login with token-based authentication
- **Boards**
  - Create, update, list, and delete boards
  - Add or remove members
- **Tasks**
  - Create, update, assign, review, and delete tasks
  - Filter tasks (e.g. "assigned to me", "reviewing")
- **Comments**
  - Add comments to tasks
  - Delete comments (only by the author)

---

## Installation & Setup

### Requirements
- Python 3.10+
- Django 5+
- Django REST Framework

### Setup Steps

```bash
# Clone repository
git clone https://github.com/yourusername/kanmind.git
cd kanmind

# Create virtual environment
python -m venv env
source env/bin/activate  # on Linux/Mac
env\Scripts\activate     # on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

API will be available at:
👉 http://127.0.0.1:8000/api/

Authentication
Register

POST /api/registration/
Create a new user.

Login

POST /api/login/
Authenticate a user and receive a token.

Boards

GET /api/boards/ → List boards where the user is owner or member

POST /api/boards/ → Create a new board

GET /api/boards/{board_id}/ → Retrieve details + tasks

PATCH /api/boards/{board_id}/ → Update members/title

DELETE /api/boards/{board_id}/ → Delete a board (only owner)

Tasks

POST /api/tasks/ → Create task

PATCH /api/tasks/{task_id}/ → Update task

DELETE /api/tasks/{task_id}/ → Delete task

GET /api/tasks/assigned-to-me/ → Tasks assigned to current user

GET /api/tasks/reviewing/ → Tasks where user is reviewer

Comments

GET /api/tasks/{task_id}/comments/ → List comments for a task

POST /api/tasks/{task_id}/comments/ → Add a comment

DELETE /api/tasks/{task_id}/comments/{comment_id}/ → Delete a comment (only the author)

Permissions

Authentication required for all board, task, and comment actions

Board owner → can update/delete the board

Task assignee/creator/board members → can view/edit related tasks

Comment author → only they can delete their comment

Status Codes

200 → Success

201 → Resource created

204 → Resource deleted

400 → Invalid request

401 → Unauthorized (login required)

403 → Forbidden (not enough permissions)

404 → Resource not found

500 → Internal server error

License

This project is licensed under the MIT License.
