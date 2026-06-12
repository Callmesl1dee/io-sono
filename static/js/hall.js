// Глобальные переменные
let currentDate = new Date().toISOString().split('T')[0];
let currentTableId = null;
let selectedSlotTime = null;

document.addEventListener('DOMContentLoaded', () => {
    // Инициализируем карту столов
    initHallMap();
});

async function initHallMap() {
    const layer = document.getElementById('tables-layer');
    if (!layer) return;

    try {
        layer.innerHTML = '<p style="color:white; text-align:center; margin-top: 30%;">Загрузка столов...</p>';
        const res = await fetch('/api/tables/');
        const tables = await res.json();
        layer.innerHTML = '';

        tables.forEach(table => {
            const tableEl = document.createElement('div');
            tableEl.className = 'table-skeleton';
            tableEl.dataset.id = table.id;
            tableEl.style.left = `${table.x}%`;
            tableEl.style.top = `${table.y}%`;
            tableEl.textContent = table.number;

            tableEl.addEventListener('click', () => {
                if (!tableEl.classList.contains('busy')) {
                    openPopup(table.id, table.number);
                }
            });

            layer.appendChild(tableEl);
        });

        // Загружаем статус занятости столов
        await loadTableStatus();
    } catch(e) {
        console.error('Ошибка инициализации карты столов:', e);
        layer.innerHTML = '<p style="color:red; text-align:center; margin-top: 30%;">Ошибка загрузки карты</p>';
    }
}

async function loadTableStatus() {
    try {
        const res = await fetch(`/api/tables-status/?date=${currentDate}`);
        const busyTables = await res.json();
        
        document.querySelectorAll('.table-skeleton').forEach(tableEl => {
            const id = parseInt(tableEl.dataset.id);
            if (busyTables.includes(id)) {
                tableEl.classList.add('busy');
            } else {
                tableEl.classList.remove('busy');
            }
        });
    } catch(e) {
        console.error('Ошибка загрузки статусов столов:', e);
    }
}

// --- ФУНКЦИИ ДЛЯ ПОПАПА ---
window.openPopup = function(id, number) {
    currentTableId = id;
    selectedSlotTime = null;
    const bookBtn = document.getElementById('book-now-btn');
    if (bookBtn) bookBtn.style.display = 'none';
    
    const titleEl = document.getElementById('popup-title');
    if (titleEl) titleEl.textContent = `Стол №${number}`;
    
    const popupEl = document.getElementById('table-popup');
    if (popupEl) popupEl.style.display = 'block';
    
    loadSlots();
};

window.closePopup = function() {
    const popupEl = document.getElementById('table-popup');
    if (popupEl) popupEl.style.display = 'none';
    
    currentTableId = null;
    selectedSlotTime = null;
    
    const bookBtn = document.getElementById('book-now-btn');
    if (bookBtn) bookBtn.style.display = 'none';
};

window.changeDate = function(days) {
    let d = new Date(currentDate);
    d.setDate(d.getDate() + days);
    currentDate = d.toISOString().split('T')[0];
    
    // Перезагружаем статусы на карте для новой даты
    loadTableStatus();
    // Перезагружаем слоты в попапе
    loadSlots();
};

async function loadSlots() {
    const container = document.getElementById('popup-slots');
    if (!container) return;
    
    const dateDisplay = document.getElementById('popup-date-display');
    if (dateDisplay) {
        dateDisplay.textContent = new Date(currentDate).toLocaleDateString('ru-RU');
    }
    
    container.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:white;">Загрузка...</div>';
    
    try {
        const res = await fetch(`/api/slots/?table=${currentTableId}&date=${currentDate}`);
        const slots = await res.json();
        container.innerHTML = '';
        
        slots.forEach(s => {
            const btn = document.createElement('button');
            btn.className = `slot-btn ${s.is_busy ? 'busy' : 'free'}`;
            btn.textContent = s.time; // "10:00-12:00"
            if (!s.is_busy) {
                btn.onclick = () => {
                    document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');
                    // Сохраняем выбранное время
                    selectedSlotTime = s.time; 
                    const bookBtn = document.getElementById('book-now-btn');
                    if (bookBtn) bookBtn.style.display = 'block';
                };
            }
            container.appendChild(btn);
        });
    } catch(e) {
        console.error('Ошибка загрузки слотов:', e);
        container.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:red;">Ошибка</div>';
    }
}

window.bookTable = function() {
    if (!currentTableId || !selectedSlotTime) return;
    // Перенаправляем на страницу бронирования с GET-параметрами
    window.location.href = `/reservation/?table=${currentTableId}&date=${currentDate}&time=${selectedSlotTime}`;
};