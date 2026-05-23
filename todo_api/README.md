# Todo API with Timers

A high-performance Python FastAPI application for managing todo lists with timers. Built with focus on response time and stability using an in-memory database.

## Features

- **User Authentication**: Signup, signin with JWT tokens
- **Project Management**: Create projects, add partners
- **Task Management**: Create tasks, assign to partners, track progress
- **Timer System**: Start/stop timers on tasks, track work duration
- **Thread-Safe**: All operations use locks for concurrent access safety
- **In-Memory DB**: Maximum performance with no I/O overhead

## Quick Start

```bash
# Activate virtual environment
cd todo_api
source venv/bin/activate

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /signup` - Register a new user
- `POST /token` - Login and get access token

### Projects
- `POST /projects` - Create a new project
- `GET /projects` - List all projects you're a partner in
- `GET /projects/{project_id}` - Get project details
- `POST /projects/{project_id}/partners` - Add a partner (owner only)

### Tasks
- `POST /tasks` - Create a new task
- `GET /projects/{project_id}/tasks` - List all tasks in a project
- `PATCH /tasks/{task_id}` - Update a task
- `POST /tasks/{task_id}/start` - Start working on a task (starts timer)
- `POST /tasks/{task_id}/complete` - Mark task as complete (stops timer)
- `GET /tasks/{task_id}/timer` - Get current timer status

### Health
- `GET /health` - Health check endpoint

## Example Usage

### 1. Sign up a user
```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"secret","email":"john@example.com"}'
```

### 2. Login and get token
```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=secret"
```

### 3. Create a project
```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"My Project","description":"Test project"}'
```

### 4. Create a task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"Fix bug","project_id":"PROJECT_ID"}'
```

### 5. Start timer on task
```bash
curl -X POST http://localhost:8000/tasks/TASK_ID/start \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Complete task
```bash
curl -X POST http://localhost:8000/tasks/TASK_ID/complete \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Performance Considerations

- **In-Memory Storage**: Uses Python dictionaries for O(1) lookups
- **Thread Safety**: All operations protected by threading.Lock
- **Async Operations**: FastAPI async handlers for non-blocking I/O
- **Minimal Dependencies**: Only essential packages installed
- **JWT Caching**: Token validation is fast with jose library

## Security Notes

⚠️ **For Production**: 
- Change `SECRET_KEY` to a secure random value
- Add rate limiting
- Enable CORS properly
- Add input validation/sanitization
- Consider persistent storage instead of in-memory

## License

MIT
