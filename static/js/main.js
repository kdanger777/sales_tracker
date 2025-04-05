// Global variables
let timer;
let seconds = 0;
let activeShiftId = null;
let leads = [];

// DOM elements
const timerDisplay = document.getElementById('timer');
const leadCount = document.getElementById('lead-count');
const startShiftBtn = document.getElementById('start-shift-btn');
const endShiftBtn = document.getElementById('end-shift-btn');
const logLeadBtn = document.getElementById('log-lead-btn');

// Timer functions
function startTimer() {
    timer = setInterval(() => {
        seconds++;
        updateTimerDisplay();
        updateCurrentPace();
    }, 1000);
}

function stopTimer() {
    clearInterval(timer);
}

function updateTimerDisplay() {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    timerDisplay.textContent = 
        `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// API functions
async function startShift() {
    try {
        const response = await fetch('/api/shift/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        activeShiftId = data.shift_id;
        
        // Update UI
        startShiftBtn.style.display = 'none';
        endShiftBtn.style.display = 'block';
        logLeadBtn.disabled = false;
        
        // Start timer
        startTimer();
        
    } catch (error) {
        console.error('Error starting shift:', error);
        alert('Failed to start shift');
    }
}

async function endShift() {
    try {
        const response = await fetch('/api/shift/end', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ shift_id: activeShiftId })
        });
        
        // Update UI
        stopTimer();
        startShiftBtn.style.display = 'block';
        endShiftBtn.style.display = 'none';
        logLeadBtn.disabled = true;
        
        // Reset
        seconds = 0;
        leads = [];
        leadCount.textContent = '0';
        updateTimerDisplay();
        
        // Update stats
        loadStats();
        
        // Show shift summary
        alert(`Shift completed! You logged ${leads.length} leads.`);
        
    } catch (error) {
        console.error('Error ending shift:', error);
        alert('Failed to end shift');
    }
}

async function logLead() {
    try {
        const response = await fetch('/api/lead/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                shift_id: activeShiftId,
                notes: ''
            })
        });
        
        const data = await response.json();
        leads.push(data);
        
        // Update lead count
        leadCount.textContent = leads.length;
        
        // Update pace
        updateCurrentPace();
        
    } catch (error) {
        console.error('Error logging lead:', error);
        alert('Failed to log lead');
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Update stats display
        document.getElementById('total-leads').textContent = data.total_leads;
        document.getElementById('avg-leads').textContent = data.avg_leads_per_shift.toFixed(1);
        document.getElementById('avg-time').textContent = 
            `${Math.round(data.avg_time_per_lead / 60)} min`;
        
        // Create time distribution chart
        createTimeChart(data.time_distribution);
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateCurrentPace() {
    if (leads.length > 0) {
        const minutesPerLead = (seconds / 60) / leads.length;
        document.getElementById('current-pace').textContent = 
            `${minutesPerLead.toFixed(1)} min/lead`;
    }
}

function createTimeChart(timeData) {
    const hours = Object.keys(timeData);
    const counts = Object.values(timeData);
    
    const data = [{
        x: hours.map(h => `${h}:00`),
        y: counts,
        type: 'bar'
    }];
    
    const layout = {
        title: 'Lead Distribution by Hour',
        xaxis: { title: 'Time of Day' },
        yaxis: { title: 'Number of Leads' }
    };
    
    Plotly.newPlot('time-chart', data, layout);
}

// Add performance comparison chart

function createComparisonChart(todayLeads, avgLeads) {
    const data = [{
        x: ['Today', 'Average'],
        y: [todayLeads, avgLeads],
        type: 'bar',
        marker: {
            color: ['#72B7B2', '#54A24B']
        }
    }];
    
    const layout = {
        title: 'Today vs Average Performance',
        yaxis: { title: 'Number of Leads' }
    };
    
    Plotly.newPlot('comparison-chart', data, layout);
}

function createDayOfWeekChart(shifts) {
    // Group leads by day of week
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayCount = Array(7).fill(0);
    
    shifts.forEach(shift => {
        const date = new Date(shift.start_time);
        const dayOfWeek = date.getDay();
        dayCount[dayOfWeek] += shift.lead_count;
    });
    
    const data = [{
        x: dayNames,
        y: dayCount,
        type: 'bar',
        marker: {color: '#4C78A8'}
    }];
    
    const layout = {
        title: 'Leads by Day of Week',
        xaxis: { title: 'Day' },
        yaxis: { title: 'Number of Leads' }
    };
    
    Plotly.newPlot('day-chart', data, layout);
}

function createProductivityTrendChart(shifts) {
    // Sort shifts by date
    const sortedShifts = [...shifts].sort((a, b) => 
        new Date(a.start_time) - new Date(b.start_time));
    
    const dates = sortedShifts.map(shift => new Date(shift.start_time).toLocaleDateString());
    const leadsPerHour = sortedShifts.map(shift => {
        const durationHours = shift.duration / 3600;
        return durationHours > 0 ? shift.lead_count / durationHours : 0;
    });
    
    const data = [{
        x: dates,
        y: leadsPerHour,
        type: 'scatter',
        mode: 'lines+markers',
        line: {shape: 'spline', smoothing: 1.3}
    }];
    
    const layout = {
        title: 'Productivity Trend (Leads per Hour)',
        xaxis: { title: 'Date' },
        yaxis: { title: 'Leads per Hour' }
    };
    
    Plotly.newPlot('trend-chart', data, layout);
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    startShiftBtn.addEventListener('click', startShift);
    endShiftBtn.addEventListener('click', endShift);
    logLeadBtn.addEventListener('click', logLead);
    
    // Init
    loadStats();
});
