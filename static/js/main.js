// Smart Attendance Tracker - Main JavaScript

// Global Variables
let inactivityTimer;
let activityTimer;
let tabSwitchCount = 0;
let isTabActive = true;
let videoStream = null;

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', function() {
    initChatbot();
    initTabDetection();
    initInactivityDetection();
    initFaceCapture();
    initVideoPlayer();
    initMCQTest();
    animateStats();
});

// ==================== CHATBOT FUNCTIONALITY ====================
function initChatbot() {
    const toggle = document.querySelector('.chatbot-toggle');
    const container = document.querySelector('.chatbot-container');
    const close = document.querySelector('.chatbot-close');
    const input = document.querySelector('.chatbot-input input');
    const sendBtn = document.querySelector('.chatbot-input button');

    if (!toggle) return;

    toggle.addEventListener('click', () => {
        container.classList.toggle('active');
    });

    if (close) {
        close.addEventListener('click', () => {
            container.classList.remove('active');
        });
    }

    if (sendBtn && input) {
        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
}

async function sendMessage() {
    const input = document.querySelector('.chatbot-input input');
    const messagesContainer = document.querySelector('.chatbot-messages');
    
    if (!input || !input.value.trim()) return;

    const userMessage = input.value.trim();
    
    // Add user message
    addMessage(userMessage, 'user');
    input.value = '';

    // Show typing indicator
    const typingMsg = addMessage('Typing...', 'bot');

    try {
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMessage })
        });
        
        const data = await response.json();
        
        // Remove typing and add response
        typingMsg.remove();
        addMessage(data.response, 'bot');
    } catch (error) {
        typingMsg.remove();
        addMessage('Sorry, something went wrong. Please try again.', 'bot');
    }
}

function addMessage(text, sender) {
    const messagesContainer = document.querySelector('.chatbot-messages');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return messageDiv;
}

// ==================== TAB SWITCHING DETECTION ====================
function initTabDetection() {
    // Check if user is on dashboard page
    if (!document.querySelector('.dashboard-page')) return;

    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // User switched tab
            tabSwitchCount++;
            showTabWarning();
            logActivity('tab_switch', `Tab switched ${tabSwitchCount} times`);
        } else {
            // User came back
            hideTabWarning();
        }
    });

    // Also detect window blur
    window.addEventListener('blur', function() {
        tabSwitchCount++;
        showTabWarning();
        logActivity('window_blur', 'Window lost focus');
    });

    window.addEventListener('focus', function() {
        hideTabWarning();
    });
}

function showTabWarning() {
    const warning = document.querySelector('.tab-warning');
    if (warning) {
        warning.classList.add('active');
    }
}

function hideTabWarning() {
    const warning = document.querySelector('.tab-warning');
    if (warning) {
        warning.classList.remove('active');
    }
}

// ==================== INACTIVITY DETECTION ====================
function initInactivityDetection() {
    if (!document.querySelector('.dashboard-page')) return;

    // Reset timer on user activity
    document.addEventListener('mousemove', resetInactivityTimer);
    document.addEventListener('keypress', resetInactivityTimer);
    document.addEventListener('click', resetInactivityTimer);
    document.addEventListener('scroll', resetInactivityTimer);

    startInactivityTimer();
}

function startInactivityTimer() {
    let inactivitySeconds = 0;
    
    activityTimer = setInterval(() => {
        inactivitySeconds++;
        updateActivityIndicator(inactivitySeconds);

        // Report inactivity every 30 seconds
        if (inactivitySeconds % 30 === 0) {
            reportInactivity(inactivitySeconds);
        }
    }, 1000);
}

function resetInactivityTimer() {
    // Clear existing timer
    if (activityTimer) {
        clearInterval(activityTimer);
    }
    
    // Reset activity indicator
    const dot = document.querySelector('.activity-dot');
    if (dot) {
        dot.classList.remove('inactive');
    }

    // Log activity
    logActivity('activity', 'User is active');

    // Restart timer
    startInactivityTimer();
}

function updateActivityIndicator(seconds) {
    const indicator = document.querySelector('.activity-indicator');
    const dot = document.querySelector('.activity-dot');
    const text = document.querySelector('.activity-text');

    if (indicator) {
        indicator.classList.add('active');
        
        if (seconds > 30) {
            dot.classList.add('inactive');
            if (text) text.textContent = `Inactive: ${seconds}s`;
        } else {
            if (text) text.textContent = 'Active';
        }
    }
}

async function reportInactivity(duration) {
    try {
        await fetch('/api/inactivity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ duration: duration })
        });
    } catch (error) {
        console.error('Failed to report inactivity:', error);
    }
}

async function logActivity(type, details) {
    try {
        await fetch('/api/activity/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type, details: details })
        });
    } catch (error) {
        console.error('Failed to log activity:', error);
    }
}

// ==================== FACE CAPTURE ====================
function initFaceCapture() {
    const video = document.getElementById('videoPreview');
    const canvas = document.getElementById('captureCanvas');
    const captureBtn = document.getElementById('captureBtn');
    const statusDiv = document.getElementById('captureStatus');

    if (!video) return;

    // Start video stream
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoStream = stream;
            video.srcObject = stream;
        })
        .catch(err => {
            if (statusDiv) {
                statusDiv.innerHTML = '<div class="alert alert-danger">Camera access denied. Please enable camera permissions.</div>';
            }
        });

    if (captureBtn) {
        captureBtn.addEventListener('click', captureFace);
    }
}

async function captureFace() {
    const video = document.getElementById('videoPreview');
    const canvas = document.getElementById('captureCanvas');
    const statusDiv = document.getElementById('captureStatus');
    const subjectId = document.getElementById('subjectId')?.value;

    if (!video || !canvas) return;

    // Capture frame
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    // Get base64 data
    const faceData = canvas.toDataURL('image/jpeg').split(',')[1];

    if (statusDiv) {
        statusDiv.innerHTML = '<div class="alert alert-warning">Verifying face...</div>';
    }

    try {
        const response = await fetch('/mark_attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                face_data: faceData,
                subject_id: subjectId || 1
            })
        });

        const data = await response.json();

        if (statusDiv) {
            if (data.success) {
                const msg = data.message || 'Attendance marked successfully!';
                statusDiv.innerHTML = `<div class="alert alert-success">✓ ${msg}</div>`;
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                statusDiv.innerHTML = `<div class="alert alert-danger">✗ ${data.message}</div>`;
            }

        }
    } catch (error) {
        if (statusDiv) {
            statusDiv.innerHTML = '<div class="alert alert-danger">Error marking attendance. Please try again.</div>';
        }
    }
}

// ==================== VIDEO PLAYER ====================
function initVideoPlayer() {
    const videoPlayer = document.querySelector('.video-player');
    const videoId = document.getElementById('videoId');

    if (!videoPlayer || !videoId) return;

    const video = videoPlayer;
    let watchedSeconds = 0;
    let lastUpdate = Date.now();

    video.addEventListener('timeupdate', function() {
        const currentTime = Math.floor(video.currentTime);
        
        // Update every 5 seconds
        if (currentTime - watchedSeconds >= 5) {
            const duration = Math.floor(video.duration);
            const completed = (video.currentTime / video.duration) > 0.9;
            
            updateVideoProgress(videoId.value, currentTime, completed);
            watchedSeconds = currentTime;
        }
    });

    video.addEventListener('ended', function() {
        updateVideoProgress(videoId.value, Math.floor(video.duration), true);
    });
}

async function updateVideoProgress(videoId, duration, completed) {
    try {
        await fetch(`/video/viewed/${videoId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                duration: duration,
                completed: completed
            })
        });
    } catch (error) {
        console.error('Failed to update video progress:', error);
    }
}

// ==================== MCQ TEST ====================
function initMCQTest() {
    const submitBtn = document.getElementById('submitTestBtn');
    
    if (!submitBtn) return;

    submitBtn.addEventListener('click', submitTest);
}

async function submitTest() {
    const answers = {};
    const questions = document.querySelectorAll('.question-option');
    
    questions.forEach(question => {
        const questionId = question.dataset.questionId;
        const selected = question.querySelector('input:checked');
        
        if (selected) {
            answers[questionId] = selected.value;
        }
    });

    const testId = document.getElementById('testId')?.value;
    
    if (!testId) return;

    // Show loading
    const resultContainer = document.getElementById('testResult');
    if (resultContainer) {
        resultContainer.innerHTML = '<div class="alert alert-warning">Submitting answers...</div>';
    }

    try {
        const response = await fetch(`/test/submit/${testId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: answers })
        });

        const data = await response.json();

        if (resultContainer) {
            const percentage = Math.round((data.score / data.total) * 100);
            let message = '';
            
            if (percentage >= 80) {
                message = 'Excellent!';
            } else if (percentage >= 60) {
                message = 'Good job!';
            } else if (percentage >= 40) {
                message = 'Keep practicing!';
            } else {
                message = 'Need improvement';
            }

            resultContainer.innerHTML = `
                <div class="score-circle">
                    <div class="score-value">${data.score}/${data.total}</div>
                    <div class="score-label">${percentage}%</div>
                </div>
                <h3 style="text-align: center; margin-bottom: 20px;">${message}</h3>
                <a href="/tests" class="btn btn-primary" style="display: block; text-align: center;">Back to Tests</a>
            `;
        }
    } catch (error) {
        if (resultContainer) {
            resultContainer.innerHTML = '<div class="alert alert-danger">Error submitting test. Please try again.</div>';
        }
    }
}

// ==================== ANIMATIONS ====================
function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const target = parseInt(stat.dataset.target || 0);
        const suffix = stat.dataset.suffix || '';
        const isTime = stat.dataset.time === 'true';
        
        if (isTime) {
            // Format as time
            const hours = Math.floor(target / 3600);
            const minutes = Math.floor((target % 3600) / 60);
            stat.textContent = `${hours}h ${minutes}m`;
        } else if (target > 0) {
            // Animate number
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                stat.textContent = Math.floor(current) + suffix;
            }, 30);
        }
    });
}

// ==================== ADDITIONAL UTILITIES ====================

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format time
function formatTime(timeString) {
    if (!timeString) return '-';
    const date = new Date('2000-01-01 ' + timeString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format duration (seconds to readable)
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
}

// Calculate percentage
function calculatePercentage(value, total) {
    if (total === 0) return 0;
    return Math.round((value / total) * 100);
}

// Get status color class
function getStatusClass(status) {
    const classes = {
        'present': 'status-present',
        'absent': 'status-absent',
        'late': 'status-late'
    };
    return classes[status] || '';
}

// Get progress bar class
function getProgressClass(percentage) {
    if (percentage >= 75) return 'high';
    if (percentage >= 50) return 'medium';
    return 'low';
}

// Stop video stream when leaving page
window.addEventListener('beforeunload', function() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
    }
});

// Export functions for use in other scripts
window.SAT = {
    formatDate,
    formatTime,
    formatDuration,
    calculatePercentage,
    getStatusClass,
    getProgressClass
};

