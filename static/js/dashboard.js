// Daily Mood Check-in
(function () {
    const options   = document.getElementById('mood-options');
    const noteWrap  = document.getElementById('mood-note-wrap');
    const noteInput = document.getElementById('mood-note');
    const saveBtn   = document.getElementById('mood-save-btn');
    const feedback  = document.getElementById('mood-feedback');

    if (!options) return;

    let selectedMood = null;

    function showFeedback(msg, type) {
        feedback.textContent = msg;
        feedback.className   = 'mood-feedback ' + type;
        feedback.style.display = 'block';
    }

    function lockMoods(selectedValue) {
        document.querySelectorAll('.mood').forEach(el => {
            if (el.dataset.mood === selectedValue) {
                el.classList.add('selected');
            } else {
                el.classList.add('disabled');
            }
        });
        if (noteWrap)  noteWrap.style.display  = 'none';
    }

    // On page load — check if user already logged today
    fetch('/mood-checkin/today')
        .then(r => r.json())
        .then(data => {
            if (data.mood) {
                lockMoods(data.mood);
                showFeedback("You've already checked in today — see you tomorrow!", 'info');
            }
        });

    // Mood selection
    document.querySelectorAll('.mood').forEach(el => {
        el.addEventListener('click', () => {
            if (el.classList.contains('disabled')) return;

            document.querySelectorAll('.mood').forEach(m => m.classList.remove('selected'));
            el.classList.add('selected');
            selectedMood = el.dataset.mood;

            noteWrap.style.display  = 'flex';
            feedback.style.display  = 'none';
        });
    });

    // Save check-in
    saveBtn && saveBtn.addEventListener('click', () => {
        if (!selectedMood) return;

        saveBtn.disabled    = true;
        saveBtn.textContent = 'Saving…';

        fetch('/mood-checkin', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                mood: selectedMood,
                note: noteInput ? noteInput.value.trim() : ''
            })
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success' || data.status === 'already_logged') {
                lockMoods(selectedMood);
                showFeedback(
                    data.status === 'success'
                        ? `Check-in saved! Feeling ${selectedMood} today.`
                        : "You've already checked in today — see you tomorrow!",
                    data.status === 'success' ? 'success' : 'info'
                );
            } else {
                showFeedback('Something went wrong. Please try again.', 'error');
                saveBtn.disabled    = false;
                saveBtn.textContent = 'Save check-in';
            }
        })
        .catch(() => {
            showFeedback('Network error. Please try again.', 'error');
            saveBtn.disabled    = false;
            saveBtn.textContent = 'Save check-in';
        });
    });
})();

// Wellness tips carousel
const tipItems   = document.querySelectorAll('.tip-item');
const tipCurrent = document.getElementById('tip-current');
const tipPrev    = document.getElementById('tip-prev');
const tipNext    = document.getElementById('tip-next');

if (tipItems.length > 1) {
    let current = 0;

    function showTip(index) {
        tipItems.forEach(t => t.classList.remove('active'));
        tipItems[index].classList.add('active');
        if (tipCurrent) tipCurrent.textContent = index + 1;
    }

    tipNext && tipNext.addEventListener('click', () => {
        current = (current + 1) % tipItems.length;
        showTip(current);
    });

    tipPrev && tipPrev.addEventListener('click', () => {
        current = (current - 1 + tipItems.length) % tipItems.length;
        showTip(current);
    });

    setInterval(() => {
        current = (current + 1) % tipItems.length;
        showTip(current);
    }, 8000);
}

// Mood Trend Chart
(function () {
    const el = document.getElementById('mood-chart-data');
    if (!el) return;

    const data   = JSON.parse(el.textContent);
    const canvas = document.getElementById('moodChart');
    if (!canvas) return;

    const pointColors = data.scores.map(s => {
        if (s === null) return 'transparent';
        if (s >= 5) return '#f6c90e';
        if (s >= 4) return '#f48fb1';
        if (s >= 3) return '#80cbc4';
        if (s >= 2) return '#90b4f0';
        return '#ef9a9a';
    });

    const safeScores = data.scores.map(s => (s === null ? NaN : s));

    new Chart(canvas, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Mood',
                data: safeScores,
                borderColor: '#80cbc4',
                borderWidth: 2,
                pointBackgroundColor: pointColors,
                pointBorderColor: pointColors,
                pointRadius: 6,
                pointHoverRadius: 8,
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(128, 203, 196, 0.08)',
                spanGaps: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0.5, max: 5.5,
                    ticks: {
                        stepSize: 1,
                        callback: val => data.emotionLabel[Math.round(val)] || '',
                        font: { size: 11 },
                        color: '#90b4b6',
                    },
                    grid: { color: 'rgba(0,0,0,0.05)' },
                },
                x: {
                    ticks: { font: { size: 11 }, color: '#90b4b6', maxRotation: 45 },
                    grid: { display: false },
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const emotion = data.emotions[ctx.dataIndex];
                            const score   = data.scores[ctx.dataIndex];
                            const label   = data.emotionLabel[score] || '';
                            return emotion ? ` ${label} (${emotion})` : ' No data';
                        }
                    }
                }
            }
        }
    });
})();