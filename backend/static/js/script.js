// ===== DASHBOARD FUNCTIONALITY =====

let detectionHistory = [];
let sessionStartTime = Date.now();
let detectionCount = 0;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 ASL Translator Dashboard Initialized');
    
    // Initialize components
    initializeAlphabetGrid();
    initializeSessionTimer();
    initializeCameraFeed();
    initializeGestureButtons();
    
    // Start updates
    startLetterUpdates();
    startStatsUpdates();
    
    // Update current time
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
});

// ===== CAMERA FUNCTIONS =====

function initializeCameraFeed() {
    const cameraFeed = document.getElementById('cameraFeed');
    const overlayText = document.getElementById('overlayText');
    
    if (cameraFeed) {
        cameraFeed.onload = function() {
            console.log('✅ Camera feed loaded successfully');
            overlayText.textContent = 'Camera active - Show your hand';
            overlayText.style.color = '#10b981';
        };
        
        cameraFeed.onerror = function() {
            console.error('❌ Camera feed error');
            overlayText.textContent = 'Camera unavailable - Check connection';
            overlayText.style.color = '#ef4444';
        };
    }
}

function refreshCamera() {
    const cameraFeed = document.getElementById('cameraFeed');
    if (cameraFeed) {
        const currentSrc = cameraFeed.src;
        cameraFeed.src = currentSrc.split('?')[0] + '?t=' + Date.now();
        
        // Show notification
        showNotification('Camera refreshed', 'success');
    }
}

function toggleFullscreen() {
    const elem = document.documentElement;
    
    if (!document.fullscreenElement) {
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) {
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) {
            elem.msRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
}

function captureFrame() {
    const cameraFeed = document.getElementById('cameraFeed');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = cameraFeed.videoWidth || cameraFeed.naturalWidth || 640;
    canvas.height = cameraFeed.videoHeight || cameraFeed.naturalHeight || 480;
    
    ctx.drawImage(cameraFeed, 0, 0, canvas.width, canvas.height);
    
    // Add timestamp
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(10, canvas.height - 40, 300, 30);
    ctx.fillStyle = 'white';
    ctx.font = '14px Arial';
    ctx.fillText(`ASL Translator - ${new Date().toLocaleString()}`, 20, canvas.height - 20);
    
    // Create download link
    const link = document.createElement('a');
    link.download = `asl-capture-${Date.now()}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
    
    showNotification('Frame captured successfully', 'success');
}

// ===== LETTER DETECTION FUNCTIONS =====

function startLetterUpdates() {
    // Update letter every 1 second
    setInterval(updateCurrentLetter, 1000);
    
    // Initial update
    updateCurrentLetter();
}

function updateCurrentLetter() {
    fetch('/get_letter')
        .then(response => {
            if (!response.ok) {
                throw new Error('Not authenticated');
            }
            return response.json();
        })
        .then(data => {
            if (data.letter && data.letter.trim() !== '') {
                updateLetterDisplay(data.letter);
                updateHistory(data.letter);
                updateStats();
            }
        })
        .catch(error => {
            console.log('Letter update error:', error);
        });
}

function updateLetterDisplay(letter) {
    const letterElement = document.getElementById('detectedLetter');
    const confidenceElement = document.getElementById('confidenceValue');
    
    if (letterElement) {
        // Animate letter change
        letterElement.style.transform = 'scale(1.2)';
        letterElement.style.opacity = '0.8';
        
        setTimeout(() => {
            letterElement.textContent = letter;
            letterElement.style.transform = 'scale(1)';
            letterElement.style.opacity = '1';
            
            // Highlight in alphabet grid
            highlightLetterInGrid(letter);
        }, 150);
    }
    
    if (confidenceElement) {
        // Simulate confidence (in real app, this would come from server)
        const confidence = 85 + Math.floor(Math.random() * 15);
        confidenceElement.textContent = `${confidence}%`;
        confidenceElement.style.color = confidence > 90 ? '#10b981' : 
                                      confidence > 80 ? '#f59e0b' : '#ef4444';
    }
    
    // Update response time
    const responseTimeElement = document.getElementById('responseTime');
    if (responseTimeElement) {
        const time = 20 + Math.floor(Math.random() * 50);
        responseTimeElement.textContent = `${time}ms`;
    }
}

function updateHistory(letter) {
    const historyList = document.getElementById('historyList');
    
    if (!historyList) return;
    
    // Add to history array
    detectionHistory.unshift({
        letter: letter,
        time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    });
    
    // Keep only last 5 items
    if (detectionHistory.length > 5) {
        detectionHistory.pop();
    }
    
    // Update detection count
    detectionCount++;
    document.getElementById('detectionCount').textContent = detectionCount;
    
    // Update history display
    historyList.innerHTML = '';
    
    detectionHistory.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item fade-in';
        historyItem.innerHTML = `
            <span class="history-letter">${item.letter}</span>
            <span class="history-time">${item.time}</span>
        `;
        historyList.appendChild(historyItem);
    });
}

// ===== ALPHABET GRID FUNCTIONS =====

function initializeAlphabetGrid() {
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const grid = document.getElementById('alphabetGrid');
    
    if (!grid) return;
    
    grid.innerHTML = '';
    
    for (let i = 0; i < alphabet.length; i++) {
        const letter = alphabet[i];
        const cell = document.createElement('div');
        cell.textContent = letter;
        cell.title = `ASL Letter ${letter}`;
        cell.dataset.letter = letter;
        
        cell.addEventListener('click', function() {
            showLetterInfo(letter);
        });
        
        grid.appendChild(cell);
    }
}

function highlightLetterInGrid(letter) {
    const allCells = document.querySelectorAll('#alphabetGrid div');
    
    // Remove active class from all
    allCells.forEach(cell => {
        cell.classList.remove('active');
    });
    
    // Add active class to current letter
    const activeCell = document.querySelector(`#alphabetGrid div[data-letter="${letter}"]`);
    if (activeCell) {
        activeCell.classList.add('active');
        
        // Scroll into view if needed
        activeCell.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
            inline: 'center'
        });
    }
}

function showLetterInfo(letter) {
    const info = {
        'A': '✊ Fist - All fingers closed',
        'B': '🖐️ Flat hand - All fingers extended',
        'C': '👌 C shape - Curved fingers',
        'D': '👆 Pointing - Index finger extended',
        'E': '🤚 Bent fingers - All fingers bent',
        'F': '🤏 OK sign - Thumb and index touching'
    };
    
    const message = info[letter] || `ASL Letter ${letter}`;
    showNotification(message, 'info');
}

// ===== GESTURE BUTTONS =====

function initializeGestureButtons() {
    const gestureButtons = document.querySelectorAll('.gesture-btn');
    
    gestureButtons.forEach(button => {
        button.addEventListener('click', function() {
            const letter = this.dataset.letter;
            if (letter) {
                // In a real app, this would trigger a specific gesture
                showNotification(`Practice gesture for letter ${letter}`, 'info');
                
                // Simulate detection
                setTimeout(() => {
                    updateLetterDisplay(letter);
                    updateHistory(letter);
                }, 500);
            }
        });
    });
}

// ===== STATISTICS FUNCTIONS =====

function initializeSessionTimer() {
    updateSessionTime();
    setInterval(updateSessionTime, 1000);
}

function updateSessionTime() {
    const elapsed = Date.now() - sessionStartTime;
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    
    const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    document.getElementById('sessionTime').textContent = timeString;
}

function startStatsUpdates() {
    setInterval(updateStats, 2000);
}

function updateStats() {
    // Update accuracy (simulated)
    const accuracyElement = document.getElementById('accuracyRate');
    if (accuracyElement) {
        const accuracy = 90 + Math.floor(Math.random() * 10);
        accuracyElement.textContent = `${accuracy}%`;
    }
    
    // Update frame rate (simulated)
    const frameRateElement = document.getElementById('frameRate');
    if (frameRateElement) {
        const fps = 25 + Math.floor(Math.random() * 10);
        frameRateElement.textContent = `${fps} FPS`;
    }
}

// ===== UTILITY FUNCTIONS =====

function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    const dateString = now.toLocaleDateString();
    
    document.getElementById('currentTime').textContent = `${dateString} ${timeString}`;
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} slide-up`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 30px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 9999;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        max-width: 400px;
        animation: slideUp 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100px)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

function getNotificationColor(type) {
    switch(type) {
        case 'success': return 'linear-gradient(135deg, #10b981, #34d399)';
        case 'error': return 'linear-gradient(135deg, #ef4444, #f87171)';
        case 'warning': return 'linear-gradient(135deg, #f59e0b, #fbbf24)';
        default: return 'linear-gradient(135deg, #6366f1, #8b5cf6)';
    }
}

// ===== EVENT LISTENERS =====

// Fullscreen change
document.addEventListener('fullscreenchange', updateFullscreenButton);
document.addEventListener('webkitfullscreenchange', updateFullscreenButton);
document.addEventListener('msfullscreenchange', updateFullscreenButton);

function updateFullscreenButton() {
    const button = document.querySelector('[onclick="toggleFullscreen()"]');
    const icon = button.querySelector('i');
    
    if (document.fullscreenElement || 
        document.webkitFullscreenElement || 
        document.msFullscreenElement) {
        icon.className = 'fas fa-compress';
        button.querySelector('span').textContent = 'Exit Fullscreen';
    } else {
        icon.className = 'fas fa-expand';
        button.querySelector('span').textContent = 'Fullscreen';
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // F5 or Ctrl+R to refresh camera
    if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
        e.preventDefault();
        refreshCamera();
    }
    
    // Escape to exit fullscreen
    if (e.key === 'Escape' && document.fullscreenElement) {
        toggleFullscreen();
    }
    
    // Number keys 1-6 for quick gestures
    if (e.key >= '1' && e.key <= '6') {
        const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
        const letter = letters[parseInt(e.key) - 1];
        showLetterInfo(letter);
    }
});

// ===== PAGE VISIBILITY =====
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('Page hidden - pausing updates');
    } else {
        console.log('Page visible - resuming updates');
        updateCurrentLetter();
    }
});

// ===== INITIAL LOAD ANIMATION =====
window.addEventListener('load', function() {
    document.body.classList.add('loaded');
    
    // Show welcome message
    setTimeout(() => {
        showNotification('Welcome to ASL Translator! Ready for detection.', 'success');
    }, 1000);
});