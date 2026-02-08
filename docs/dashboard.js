// dashboard.js - Live data updates for tracker
// Fetches real-time data from dashboard_data.json

let updateCount = 0;

async function fetchLiveData() {
    try {
        const response = await fetch('dashboard_data.json?' + Date.now());
        const data = await response.json();
        updateDashboard(data);
        updateCount++;
    } catch (error) {
        console.log('Using static data (controller not running)');
    }
}

function updateDashboard(data) {
    // Update portfolio metrics
    if (data.portfolio) {
        document.getElementById('deployed-capital').textContent = '$' + data.portfolio.deployed.toFixed(2);
        document.getElementById('remaining-capital').textContent = '$' + data.portfolio.remaining.toFixed(2);
        document.getElementById('potential-return').textContent = '+$' + data.portfolio.potential_return.toFixed(2);
    }
    
    // Update positions
    if (data.positions && data.positions.length >= 2) {
        // Position 1
        document.getElementById('pos1-potential').textContent = '+$' + data.positions[0].potential.toFixed(2) + ' (+' + data.positions[0].roi.toLocaleString() + '%)';
        document.getElementById('pos1-days').textContent = data.positions[0].days_remaining;
        
        // Position 2
        document.getElementById('pos2-potential').textContent = '+$' + data.positions[1].potential.toFixed(2) + ' (+' + data.positions[1].roi.toLocaleString() + '%)';
        document.getElementById('pos2-days').textContent = data.positions[1].days_remaining;
    }
    
    // Update activity feed
    if (data.activity) {
        const activityContainer = document.getElementById('activity-feed');
        activityContainer.innerHTML = '';
        
        data.activity.slice(0, 5).forEach(item => {
            const div = document.createElement('div');
            div.className = 'activity-item';
            div.innerHTML = `
                <div class="activity-time">${item.time}</div>
                <div class="activity-message">${item.message}</div>
            `;
            activityContainer.appendChild(div);
        });
    }
    
    // Update last updated time
    if (data.timestamp) {
        const time = new Date(data.timestamp).toLocaleTimeString();
        document.getElementById('last-updated').textContent = time;
    }
}

// Initial load
fetchLiveData();

// Auto-refresh every 10 seconds
setInterval(fetchLiveData, 10000);

console.log('Dashboard live updater active - refreshing every 10 seconds');