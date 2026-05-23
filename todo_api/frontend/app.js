// API Configuration
const API_BASE = 'http://localhost:8000';

// State Management
const state = {
    token: localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    projects: [],
    tasks: [],
    currentProject: null,
    timers: {}
};

// DOM Elements
const elements = {
    authSection: document.getElementById('auth-section'),
    mainSection: document.getElementById('main-section'),
    authForm: document.getElementById('auth-form'),
    authTitle: document.getElementById('auth-title'),
    authBtn: document.getElementById('auth-btn'),
    toggleAuth: document.getElementById('toggle-auth'),
    authError: document.getElementById('auth-error'),
    usernameInput: document.getElementById('username'),
    passwordInput: document.getElementById('password'),
    userDisplay: document.getElementById('user-display'),
    logoutBtn: document.getElementById('logout-btn'),
    projectsView: document.getElementById('projects-view'),
    tasksView: document.getElementById('tasks-view'),
    projectsList: document.getElementById('projects-list'),
    tasksList: document.getElementById('tasks-list'),
    newProjectBtn: document.getElementById('new-project-btn'),
    newTaskBtn: document.getElementById('new-task-btn'),
    currentProjectTitle: document.getElementById('current-project-title'),
    tabBtns: document.querySelectorAll('.tab-btn'),
    modalOverlay: document.getElementById('modal-overlay'),
    modalTitle: document.getElementById('modal-title'),
    modalForm: document.getElementById('modal-form'),
    modalCancel: document.getElementById('modal-cancel'),
    modalSubmit: document.getElementById('modal-submit')
};

let isSignUp = false;

// Initialize App
function init() {
    if (state.token && state.user) {
        showMainApp();
        loadProjects();
    } else {
        showAuth();
    }
    startTimerUpdates();
}

// Auth Functions
async function handleAuth(e) {
    e.preventDefault();
    const username = elements.usernameInput.value;
    const password = elements.passwordInput.value;

    try {
        const endpoint = isSignUp ? '/signup' : '/token';
        const body = isSignUp 
            ? { username, password } 
            : { username, password };

        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Authentication failed');
        }

        if (isSignUp) {
            // Auto-login after signup
            await login(username, password);
        } else {
            state.token = data.access_token;
            state.user = { username };
            localStorage.setItem('token', state.token);
            localStorage.setItem('user', JSON.stringify(state.user));
            showMainApp();
            loadProjects();
        }
    } catch (error) {
        elements.authError.textContent = error.message;
    }
}

async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Login failed');

        state.token = data.access_token;
        state.user = { username };
        localStorage.setItem('token', state.token);
        localStorage.setItem('user', JSON.stringify(state.user));
        showMainApp();
        loadProjects();
    } catch (error) {
        elements.authError.textContent = error.message;
    }
}

function logout() {
    state.token = null;
    state.user = null;
    state.projects = [];
    state.tasks = [];
    state.currentProject = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    stopAllTimers();
    showAuth();
}

// UI Functions
function showAuth() {
    elements.authSection.classList.remove('hidden');
    elements.mainSection.classList.add('hidden');
}

function showMainApp() {
    elements.authSection.classList.add('hidden');
    elements.mainSection.classList.remove('hidden');
    elements.userDisplay.textContent = `👤 ${state.user.username}`;
}

function toggleAuthMode() {
    isSignUp = !isSignUp;
    elements.authTitle.textContent = isSignUp ? 'Sign Up' : 'Sign In';
    elements.authBtn.textContent = isSignUp ? 'Sign Up' : 'Sign In';
    elements.toggleAuth.innerHTML = isSignUp 
        ? 'Already have an account? <a href="#" id="toggle-auth">Sign In</a>'
        : "Don't have an account? <a href=\"#\" id=\"toggle-auth\">Sign Up</a>";
    
    // Rebind event listener
    document.getElementById('toggle-auth').addEventListener('click', (e) => {
        e.preventDefault();
        toggleAuthMode();
    });
    
    elements.authError.textContent = '';
}

// Projects Functions
async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE}/projects`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });

        if (!response.ok) throw new Error('Failed to load projects');

        state.projects = await response.json();
        renderProjects();
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

function renderProjects() {
    elements.projectsList.innerHTML = state.projects.map(project => `
        <div class="card">
            <h3>${escapeHtml(project.name)}</h3>
            <p>${escapeHtml(project.description || 'No description')}</p>
            <p><small>Created: ${new Date(project.created_at).toLocaleDateString()}</small></p>
            <div class="card-actions">
                <button class="btn-primary" onclick="openProject(${project.id})">Open</button>
                <button class="btn-secondary" onclick="showAddPartnerModal(${project.id})">Add Partner</button>
            </div>
        </div>
    `).join('');

    if (state.projects.length === 0) {
        elements.projectsList.innerHTML = '<p style="color: var(--text-light); text-align: center; padding: 2rem;">No projects yet. Create your first project!</p>';
    }
}

async function createProject(name, description) {
    try {
        const response = await fetch(`${API_BASE}/projects`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({ name, description })
        });

        if (!response.ok) throw new Error('Failed to create project');

        await loadProjects();
        return true;
    } catch (error) {
        alert(error.message);
        return false;
    }
}

async function addPartner(projectId, partnerUsername) {
    try {
        const response = await fetch(`${API_BASE}/projects/${projectId}/partners`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({ username: partnerUsername })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to add partner');
        }

        alert('Partner added successfully!');
        return true;
    } catch (error) {
        alert(error.message);
        return false;
    }
}

// Tasks Functions
function openProject(projectId) {
    state.currentProject = state.projects.find(p => p.id === projectId);
    if (!state.currentProject) return;

    elements.currentProjectTitle.textContent = `Tasks: ${state.currentProject.name}`;
    elements.newTaskBtn.disabled = false;
    
    // Switch to tasks view
    elements.tabBtns.forEach(btn => btn.classList.remove('active'));
    elements.tabBtns[1].classList.add('active');
    elements.projectsView.classList.add('hidden');
    elements.tasksView.classList.remove('hidden');
    
    loadTasks(projectId);
}

async function loadTasks(projectId) {
    try {
        const response = await fetch(`${API_BASE}/projects/${projectId}/tasks`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });

        if (!response.ok) throw new Error('Failed to load tasks');

        state.tasks = await response.json();
        renderTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function renderTasks() {
    elements.tasksList.innerHTML = state.tasks.map(task => {
        const timer = state.timers[task.id] || { running: false, startTime: null, elapsed: task.total_time_seconds || 0 };
        const timeStr = formatTime(timer.elapsed);
        
        return `
            <div class="task-item ${task.completed ? 'completed' : ''}">
                <div class="task-info">
                    <div class="task-title">${escapeHtml(task.title)}</div>
                    <div class="task-meta">
                        ${task.description ? escapeHtml(task.description) + ' • ' : ''}
                        Assigned to: ${task.assigned_to || 'Unassigned'} • 
                        Status: ${task.completed ? '✅ Completed' : '⏳ Pending'}
                    </div>
                </div>
                <div class="task-timer" id="timer-${task.id}">${timeStr}</div>
                <div class="task-actions">
                    ${!task.completed && !timer.running 
                        ? `<button class="btn-success" onclick="startTaskTimer(${task.id})">▶ Start</button>` 
                        : ''}
                    ${timer.running 
                        ? `<button class="btn-warning" onclick="stopTaskTimer(${task.id})">⏸ Pause</button>` 
                        : ''}
                    ${!task.completed 
                        ? `<button class="btn-primary" onclick="completeTask(${task.id})">✓ Complete</button>` 
                        : ''}
                </div>
            </div>
        `;
    }).join('');

    if (state.tasks.length === 0) {
        elements.tasksList.innerHTML = '<p style="color: var(--text-light); text-align: center; padding: 2rem;">No tasks yet. Create your first task!</p>';
    }
}

async function createTask(title, description, assignedTo) {
    if (!state.currentProject) return false;

    try {
        const response = await fetch(`${API_BASE}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({
                project_id: state.currentProject.id,
                title,
                description,
                assigned_to: assignedTo || null
            })
        });

        if (!response.ok) throw new Error('Failed to create task');

        await loadTasks(state.currentProject.id);
        return true;
    } catch (error) {
        alert(error.message);
        return false;
    }
}

async function completeTask(taskId) {
    try {
        // First stop the timer if running
        if (state.timers[taskId]?.running) {
            await stopTaskTimer(taskId, false);
        }

        const response = await fetch(`${API_BASE}/tasks/${taskId}/complete`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${state.token}` }
        });

        if (!response.ok) throw new Error('Failed to complete task');

        await loadTasks(state.currentProject.id);
    } catch (error) {
        alert(error.message);
    }
}

// Timer Functions
function startTimerUpdates() {
    setInterval(() => {
        Object.keys(state.timers).forEach(taskId => {
            const timer = state.timers[taskId];
            if (timer.running && timer.startTime) {
                const elapsed = timer.elapsed + (Date.now() - timer.startTime) / 1000;
                timer.elapsed = elapsed;
                
                const timerEl = document.getElementById(`timer-${taskId}`);
                if (timerEl) {
                    timerEl.textContent = formatTime(elapsed);
                }
            }
        });
    }, 100);
}

function startTaskTimer(taskId) {
    state.timers[taskId] = {
        running: true,
        startTime: Date.now(),
        elapsed: state.timers[taskId]?.elapsed || 0
    };
    renderTasks();
}

async function stopTaskTimer(taskId, reload = true) {
    const timer = state.timers[taskId];
    if (!timer || !timer.running) return;

    const elapsed = timer.elapsed + (Date.now() - timer.startTime) / 1000;
    
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}/stop-timer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({ seconds: Math.round(elapsed) })
        });

        if (!response.ok) throw new Error('Failed to stop timer');

        state.timers[taskId] = { running: false, startTime: null, elapsed: 0 };
        
        if (reload && state.currentProject) {
            await loadTasks(state.currentProject.id);
        } else {
            renderTasks();
        }
    } catch (error) {
        alert(error.message);
    }
}

function stopAllTimers() {
    Object.keys(state.timers).forEach(taskId => {
        state.timers[taskId] = { running: false, startTime: null, elapsed: 0 };
    });
}

function formatTime(seconds) {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Modal Functions
function showModal(title, formHTML, onSubmit) {
    elements.modalTitle.textContent = title;
    elements.modalForm.innerHTML = formHTML;
    elements.modalOverlay.classList.remove('hidden');

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        const success = await onSubmit(data);
        if (success) {
            closeModal();
        }
    };

    elements.modalForm.addEventListener('submit', handleSubmit);
}

function closeModal() {
    elements.modalOverlay.classList.add('hidden');
    elements.modalForm.innerHTML = '';
}

function showNewProjectModal() {
    showModal('New Project', `
        <input type="text" name="name" placeholder="Project Name" required>
        <textarea name="description" placeholder="Description (optional)" rows="3"></textarea>
    `, async (data) => {
        return await createProject(data.name, data.description || '');
    });
}

function showNewTaskModal() {
    const partners = state.currentProject?.partners || [];
    const partnerOptions = partners.length > 0 
        ? `<option value="">Unassigned</option>` + partners.map(p => 
            `<option value="${p.username}">${p.username}</option>`
          ).join('')
        : '<option value="">Unassigned</option>';

    showModal('New Task', `
        <input type="text" name="title" placeholder="Task Title" required>
        <textarea name="description" placeholder="Description (optional)" rows="3"></textarea>
        <select name="assigned_to">
            ${partnerOptions}
        </select>
    `, async (data) => {
        return await createTask(data.title, data.description || '', data.assigned_to || null);
    });
}

function showAddPartnerModal(projectId) {
    showModal('Add Partner', `
        <input type="text" name="username" placeholder="Partner Username" required>
    `, async (data) => {
        return await addPartner(projectId, data.username);
    });
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event Listeners
elements.authForm.addEventListener('submit', handleAuth);
elements.toggleAuth.addEventListener('click', (e) => {
    e.preventDefault();
    toggleAuthMode();
});
elements.logoutBtn.addEventListener('click', logout);
elements.newProjectBtn.addEventListener('click', showNewProjectModal);
elements.newTaskBtn.addEventListener('click', showNewTaskModal);
elements.modalCancel.addEventListener('click', closeModal);
elements.modalOverlay.addEventListener('click', (e) => {
    if (e.target === elements.modalOverlay) closeModal();
});

elements.tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        
        elements.tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        if (tab === 'projects') {
            elements.projectsView.classList.remove('hidden');
            elements.tasksView.classList.add('hidden');
            state.currentProject = null;
            elements.newTaskBtn.disabled = true;
        } else {
            elements.projectsView.classList.add('hidden');
            elements.tasksView.classList.remove('hidden');
        }
    });
});

// Initialize on load
init();
