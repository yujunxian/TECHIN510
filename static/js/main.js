// Timer functionality
let timerInterval;
let timeLeft = 25 * 60; // 25 minutes in seconds
let isRunning = false;

function updateTimer() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    document.getElementById('timer').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function startTimer() {
    if (!isRunning) {
        isRunning = true;
        timerInterval = setInterval(() => {
            if (timeLeft > 0) {
                timeLeft--;
                updateTimer();
            } else {
                clearInterval(timerInterval);
                isRunning = false;
                alert('Time is up! Take a break!');
            }
        }, 1000);
    }
}

function pauseTimer() {
    if (isRunning) {
        clearInterval(timerInterval);
        isRunning = false;
    }
}

function resetTimer() {
    clearInterval(timerInterval);
    isRunning = false;
    timeLeft = 25 * 60;
    updateTimer();
}

// Task list functionality
function addTask(taskText) {
    const taskList = document.getElementById('taskList');
    const taskId = Date.now().toString();
    
    const taskElement = document.createElement('div');
    taskElement.className = 'task-item';
    taskElement.dataset.taskId = taskId;
    taskElement.innerHTML = `
        <div class="flex items-center">
            <input type="checkbox" class="mr-2" onchange="toggleTask('${taskId}')">
            <span>${taskText}</span>
        </div>
        <button class="btn btn-secondary" onclick="deleteTask('${taskId}')">
            Delete
        </button>
    `;
    
    taskList.appendChild(taskElement);
    saveTasks();
}

function toggleTask(taskId) {
    const task = document.querySelector(`[data-task-id="${taskId}"]`);
    if (task) {
        task.classList.toggle('completed');
        saveTasks();
    }
}

function deleteTask(taskId) {
    const task = document.querySelector(`[data-task-id="${taskId}"]`);
    if (task) {
        task.remove();
        saveTasks();
    }
}

function saveTasks() {
    const tasks = [];
    document.querySelectorAll('#taskList .task-item').forEach(task => {
        tasks.push({
            id: task.dataset.taskId,
            text: task.querySelector('span').textContent,
            completed: task.classList.contains('completed')
        });
    });
    localStorage.setItem('tasks', JSON.stringify(tasks));
}

function loadTasks() {
    const tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
    tasks.forEach(task => {
        addTask(task.text);
        if (task.completed) {
            const taskElement = document.querySelector(`[data-task-id="${task.id}"]`);
            if (taskElement) {
                taskElement.classList.add('completed');
            }
        }
    });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Timer controls
    document.getElementById('startTimer').addEventListener('click', startTimer);
    document.getElementById('pauseTimer').addEventListener('click', pauseTimer);
    document.getElementById('resetTimer').addEventListener('click', resetTimer);

    // Task form
    document.getElementById('taskForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const taskInput = document.getElementById('taskInput');
        const taskText = taskInput.value.trim();
        if (taskText) {
            addTask(taskText);
            taskInput.value = '';
        }
    });

    // Load saved tasks
    loadTasks();
}); 