import time
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from threading import Lock

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from jose import JWTError, jwt

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Thread-safe in-memory database
class InMemoryDB:
    def __init__(self):
        self._lock = Lock()
        self.users: Dict[str, dict] = {}
        self.projects: Dict[str, dict] = {}
        self.tasks: Dict[str, dict] = {}
        self.project_partners: Dict[str, List[str]] = {}  # project_id -> [user_ids]
        self.task_timers: Dict[str, dict] = {}  # task_id -> {started_at, user_id}

    def add_user(self, user: dict):
        with self._lock:
            self.users[user["id"]] = user

    def get_user_by_username(self, username: str) -> Optional[dict]:
        with self._lock:
            for user in self.users.values():
                if user["username"] == username:
                    return user
            return None

    def get_user(self, user_id: str) -> Optional[dict]:
        with self._lock:
            return self.users.get(user_id)

    def add_project(self, project: dict):
        with self._lock:
            self.projects[project["id"]] = project
            self.project_partners[project["id"]] = []

    def get_project(self, project_id: str) -> Optional[dict]:
        with self._lock:
            return self.projects.get(project_id)

    def get_all_projects(self) -> List[dict]:
        with self._lock:
            return list(self.projects.values())

    def add_partner_to_project(self, project_id: str, user_id: str):
        with self._lock:
            if project_id not in self.project_partners:
                raise ValueError("Project not found")
            if user_id not in self.project_partners[project_id]:
                self.project_partners[project_id].append(user_id)

    def get_project_partners(self, project_id: str) -> List[str]:
        with self._lock:
            return self.project_partners.get(project_id, [])

    def is_project_partner(self, project_id: str, user_id: str) -> bool:
        with self._lock:
            partners = self.project_partners.get(project_id, [])
            return user_id in partners

    def add_task(self, task: dict):
        with self._lock:
            self.tasks[task["id"]] = task

    def get_task(self, task_id: str) -> Optional[dict]:
        with self._lock:
            return self.tasks.get(task_id)

    def get_tasks_by_project(self, project_id: str) -> List[dict]:
        with self._lock:
            return [t for t in self.tasks.values() if t["project_id"] == project_id]

    def update_task(self, task_id: str, updates: dict):
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].update(updates)

    def start_task_timer(self, task_id: str, user_id: str):
        with self._lock:
            self.task_timers[task_id] = {
                "started_at": datetime.utcnow(),
                "user_id": user_id
            }

    def stop_task_timer(self, task_id: str) -> Optional[float]:
        with self._lock:
            if task_id in self.task_timers:
                timer = self.task_timers.pop(task_id)
                duration = (datetime.utcnow() - timer["started_at"]).total_seconds()
                return duration
            return None

    def get_task_timer(self, task_id: str) -> Optional[dict]:
        with self._lock:
            return self.task_timers.get(task_id)

db = InMemoryDB()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: str
    assigned_to: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None

class PartnerAdd(BaseModel):
    user_id: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: datetime

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    project_id: str
    assigned_to: Optional[str]
    completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.get_user(user_id)
    if user is None:
        raise credentials_exception
    return user

# FastAPI app
app = FastAPI(title="Todo API with Timers", version="1.0.0")

@app.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Register a new user"""
    if db.get_user_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password": get_password_hash(user_data.password),
        "created_at": datetime.utcnow()
    }
    db.add_user(user)
    return {"id": user["id"], "username": user["username"], "email": user["email"]}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    user = db.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new project (owner is automatically added as partner)"""
    project_id = str(uuid.uuid4())
    project = {
        "id": project_id,
        "name": project_data.name,
        "description": project_data.description,
        "owner_id": current_user["id"],
        "created_at": datetime.utcnow()
    }
    db.add_project(project)
    db.add_partner_to_project(project_id, current_user["id"])
    return project

@app.get("/projects", response_model=List[ProjectResponse])
async def get_projects(current_user: dict = Depends(get_current_user)):
    """Get all projects where user is a partner"""
    all_projects = db.get_all_projects()
    user_projects = []
    for project in all_projects:
        if db.is_project_partner(project["id"], current_user["id"]):
            user_projects.append(project)
    return user_projects

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific project"""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not db.is_project_partner(project_id, current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    return project

@app.post("/projects/{project_id}/partners", status_code=status.HTTP_201_CREATED)
async def add_partner(
    project_id: str,
    partner_data: PartnerAdd,
    current_user: dict = Depends(get_current_user)
):
    """Add a partner to a project (only owner can add partners)"""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only project owner can add partners")
    
    user = db.get_user(partner_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.add_partner_to_project(project_id, partner_data.user_id)
    return {"message": "Partner added successfully"}

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new task in a project"""
    project = db.get_project(task_data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not db.is_project_partner(task_data.project_id, current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to create tasks in this project")
    
    if task_data.assigned_to:
        if not db.is_project_partner(task_data.project_id, task_data.assigned_to):
            raise HTTPException(status_code=400, detail="Assigned user must be a project partner")
    
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "title": task_data.title,
        "description": task_data.description,
        "project_id": task_data.project_id,
        "assigned_to": task_data.assigned_to,
        "completed": False,
        "created_at": datetime.utcnow(),
        "completed_at": None
    }
    db.add_task(task)
    return task

@app.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all tasks in a project"""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not db.is_project_partner(project_id, current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to view tasks in this project")
    
    return db.get_tasks_by_project(project_id)

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a task"""
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not db.is_project_partner(task["project_id"], current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    updates = {}
    if task_data.title is not None:
        updates["title"] = task_data.title
    if task_data.description is not None:
        updates["description"] = task_data.description
    if task_data.assigned_to is not None:
        if not db.is_project_partner(task["project_id"], task_data.assigned_to):
            raise HTTPException(status_code=400, detail="Assigned user must be a project partner")
        updates["assigned_to"] = task_data.assigned_to
    
    db.update_task(task_id, updates)
    updated_task = db.get_task(task_id)
    return updated_task

@app.post("/tasks/{task_id}/start", response_model=dict)
async def start_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Start working on a task (starts timer)"""
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not db.is_project_partner(task["project_id"], current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to work on this task")
    
    if task["completed"]:
        raise HTTPException(status_code=400, detail="Cannot start a completed task")
    
    # Stop existing timer if any
    db.stop_task_timer(task_id)
    
    # Start new timer
    db.start_task_timer(task_id, current_user["id"])
    
    return {"message": "Task timer started", "task_id": task_id, "started_at": datetime.utcnow().isoformat()}

@app.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a task as complete (stops timer and records duration)"""
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not db.is_project_partner(task["project_id"], current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to complete this task")
    
    if task["completed"]:
        raise HTTPException(status_code=400, detail="Task already completed")
    
    # Stop timer and get duration
    duration = db.stop_task_timer(task_id)
    
    # Mark task as complete
    updates = {
        "completed": True,
        "completed_at": datetime.utcnow()
    }
    if duration is not None:
        updates["last_work_duration"] = duration
    
    db.update_task(task_id, updates)
    updated_task = db.get_task(task_id)
    
    response = updated_task.copy()
    if duration is not None:
        response["work_duration_seconds"] = duration
    
    return response

@app.get("/tasks/{task_id}/timer", response_model=dict)
async def get_task_timer(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get current timer status for a task"""
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not db.is_project_partner(task["project_id"], current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    
    timer = db.get_task_timer(task_id)
    if not timer:
        return {"active": False, "task_id": task_id}
    
    elapsed = (datetime.utcnow() - timer["started_at"]).total_seconds()
    return {
        "active": True,
        "task_id": task_id,
        "started_at": timer["started_at"].isoformat(),
        "elapsed_seconds": elapsed,
        "user_id": timer["user_id"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
