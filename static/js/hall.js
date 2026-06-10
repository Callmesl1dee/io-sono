document.addEventListener('DOMContentLoaded', () => {
    // Добавляем обработчики на SVG столы
    document.querySelectorAll('.svg-table').forEach(tableEl => {
        const tableId = parseInt(tableEl.dataset.id);
        tableEl.addEventListener('click', () => {
            if (!tableEl.classList.contains('busy')) {
                openPopup(tableId, tableId.toString());
            }
        });
    });
    
    loadTableStatus();
});

async function loadTableStatus() {
    try {
        const res = await fetch(`/api/tables-status/?date=${currentDate}`);
        const busyTables = await res.json();
        
        document.querySelectorAll('.svg-table').forEach(tableEl => {
            const id = parseInt(tableEl.dataset.id);
            if (busyTables.includes(id)) {
                tableEl.classList.add('busy');
                tableEl.classList.remove('active');
            }
        });
    } catch(e) {
        console.error('Ошибка загрузки статусов');
    }
}