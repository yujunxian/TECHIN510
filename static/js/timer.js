let startTime;
let timerInterval;
let isRunning = false;

// 初始化计时器
function initTimer() {
    const timerElement = document.querySelector('.timer');
    const taskNameElement = document.querySelector('.task-name');
    
    // 从 URL 参数获取任务名称
    const urlParams = new URLSearchParams(window.location.search);
    const taskName = urlParams.get('task') || 'Reading';
    taskNameElement.textContent = taskName;
    
    // 设置初始时间
    timerElement.textContent = '00:00';
}

// 开始计时
function startTimer() {
    if (!isRunning) {
        startTime = Date.now();
        isRunning = true;
        timerInterval = setInterval(updateTimer, 1000);
    }
}

// 停止计时
function stopTimer() {
    if (isRunning) {
        clearInterval(timerInterval);
        isRunning = false;
    }
}

// 更新计时器显示
function updateTimer() {
    const timerElement = document.querySelector('.timer');
    const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsedTime / 60);
    const seconds = elapsedTime % 60;
    timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// 初始化 Spotify 播放器
function initSpotifyPlayer() {
    const heartBtn = document.querySelector('.heart-btn');
    const repeatBtn = document.querySelector('.repeat-btn');
    
    heartBtn.addEventListener('click', () => {
        // 处理收藏功能
        heartBtn.classList.toggle('active');
    });
    
    repeatBtn.addEventListener('click', () => {
        // 处理重复播放功能
        repeatBtn.classList.toggle('active');
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initTimer();
    initSpotifyPlayer();
    startTimer();
}); 