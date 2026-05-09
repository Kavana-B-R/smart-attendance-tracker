// Attendance Filter JS
function filterAttendance() {
    const subject = document.getElementById('filterSubject').value;
    const date = document.getElementById('filterDate').value;
    const rows = document.querySelectorAll('#attendanceTable tbody tr');
    
    let count = 0;
    
    rows.forEach(row => {
        const rowSubject = row.dataset.subject;
        const rowDate = row.dataset.date;
        
        const matchSubject = !subject || rowSubject.toLowerCase().includes(subject.toLowerCase());
        const matchDate = !date || rowDate === date;
        
        if (matchSubject && matchDate) {
            row.style.display = '';
            count++;
        } else {
            row.style.display = 'none';
        }
    });
    
    // Update counter if needed
    console.log(`${count} records match filter`);
}

function clearFilters() {
    document.getElementById('filterSubject').value = '';
    document.getElementById('filterDate').value = '';
    filterAttendance();
}

// Auto-filter on change
document.getElementById('filterSubject').addEventListener('change', filterAttendance);
document.getElementById('filterDate').addEventListener('change', filterAttendance);
