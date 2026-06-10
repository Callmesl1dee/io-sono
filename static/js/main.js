document.addEventListener('DOMContentLoaded', () => {
    
    // ========================================
    // === КОД ДРУГА: DATE/TIME PICKERS ===
    // ========================================
    
    const timePicker = document.querySelector('.time-picker');

    if (timePicker) {
        const valueLabel = timePicker.querySelector('.time-picker__value');
        const radios = timePicker.querySelectorAll('.time-picker__radio');

        radios.forEach((radio) => {
            radio.addEventListener('change', () => {
                if (radio.checked) {
                    valueLabel.textContent = radio.value;
                    valueLabel.classList.remove('is-placeholder');
                    timePicker.open = false;
                }
            });
        });
    }

    const datePicker = document.querySelector('[data-date-picker]');

    if (datePicker) {
        const hiddenInput = datePicker.querySelector('input[name="date"]');
        const valueLabel = datePicker.querySelector('.date-picker__value');
        const monthLabel = datePicker.querySelector('[data-date-month]');
        const grid = datePicker.querySelector('[data-date-grid]');
        const prevButton = datePicker.querySelector('[data-date-prev]');
        const nextButton = datePicker.querySelector('[data-date-next]');

        const monthNames = [
            'январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
            'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'
        ];

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        let currentMonth = getStartOfMonth(hiddenInput.value ? new Date(`${hiddenInput.value}T00:00:00`) : today);

        function getStartOfMonth(date) {
            return new Date(date.getFullYear(), date.getMonth(), 1);
        }

        function toIsoDate(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }

        function formatLabel(date) {
            return date.toLocaleDateString('ru-RU', {
                day: '2-digit',
                month: 'long',
                year: 'numeric'
            });
        }

        function isSameDate(left, right) {
            return left.getFullYear() === right.getFullYear()
                && left.getMonth() === right.getMonth()
                && left.getDate() === right.getDate();
        }

        function renderCalendar() {
            const year = currentMonth.getFullYear();
            const month = currentMonth.getMonth();
            const firstDay = new Date(year, month, 1);
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            const leadingEmpty = (firstDay.getDay() + 6) % 7;

            monthLabel.textContent = `${monthNames[month]} ${year}`;
            grid.innerHTML = '';

            for (let i = 0; i < leadingEmpty; i += 1) {
                const emptyCell = document.createElement('button');
                emptyCell.type = 'button';
                emptyCell.className = 'date-picker__day is-empty';
                emptyCell.tabIndex = -1;
                emptyCell.setAttribute('aria-hidden', 'true');
                emptyCell.disabled = true;
                grid.appendChild(emptyCell);
            }

            for (let day = 1; day <= daysInMonth; day += 1) {
                const date = new Date(year, month, day);
                date.setHours(0, 0, 0, 0);

                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'date-picker__day';
                button.textContent = String(day);
                button.dataset.date = toIsoDate(date);

                if (date < today) {
                    button.classList.add('is-disabled');
                    button.disabled = true;
                }

                if (isSameDate(date, today)) {
                    button.classList.add('is-today');
                }

                if (hiddenInput.value && hiddenInput.value === button.dataset.date) {
                    button.classList.add('is-selected');
                }

                button.addEventListener('click', () => {
                    if (button.disabled) return;

                    hiddenInput.value = button.dataset.date;
                    valueLabel.textContent = formatLabel(date);
                    valueLabel.classList.remove('is-placeholder');

                    datePicker.open = false;
                    renderCalendar();
                });

                grid.appendChild(button);
            }

            const firstSelectableMonth = new Date(today.getFullYear(), today.getMonth(), 1);
            prevButton.disabled = currentMonth <= firstSelectableMonth;
            prevButton.classList.toggle('is-disabled', prevButton.disabled);
        }

        datePicker.addEventListener('toggle', () => {
            if (datePicker.open) renderCalendar();
        });

        prevButton.addEventListener('click', () => {
            if (prevButton.disabled) return;
            currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1);
            renderCalendar();
        });

        nextButton.addEventListener('click', () => {
            currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1);
            renderCalendar();
        });

        if (hiddenInput.value) {
            const selectedDate = new Date(`${hiddenInput.value}T00:00:00`);
            if (!Number.isNaN(selectedDate.getTime())) {
                valueLabel.textContent = formatLabel(selectedDate);
                valueLabel.classList.remove('is-placeholder');
            }
        }

        renderCalendar();
    }
    
    // ========================================
    // === МОДАЛКА: БЕЗОПАСНОЕ ОТКРЫТИЕ ===
    // ========================================
    
    const modal = document.getElementById('dish-modal');
    
    if (modal) {
        const closeBtn = modal.querySelector('.modal-close');
        const mImgContainer = document.getElementById('modal-img-container');
        const mImg = document.getElementById('modal-img');
        const mCategory = document.getElementById('modal-category');
        const mTitle = document.getElementById('modal-title');
        const mDesc = document.getElementById('modal-desc');
        const mPrice = document.getElementById('modal-price');
        const mVolume = document.getElementById('modal-volume');
        const mAlcohol = document.getElementById('modal-alcohol');

        function openModal(card) {
            try {
                const title = card.dataset.title || '';
                const desc = card.dataset.desc || '';
                const price = card.dataset.price || '';
                const category = card.dataset.category || '';
                const volume = card.dataset.volume || '';
                const alcohol = card.dataset.alcohol || '';
                const imgSrc = card.dataset.img || '';

                mTitle.textContent = title;
                mDesc.textContent = desc;
                mPrice.textContent = price ? `${price} ₽` : '';
                mCategory.textContent = category;

                mVolume.textContent = volume ? `🥤 ${volume}` : '';
                mVolume.style.display = volume ? 'inline-block' : 'none';
                
                mAlcohol.textContent = alcohol ? `🍷 ${alcohol}` : '';
                mAlcohol.style.display = alcohol ? 'inline-block' : 'none';

                if (imgSrc) {
                    mImg.src = imgSrc;
                    mImgContainer.style.display = 'block';
                } else {
                    mImgContainer.style.display = 'none';
                }

                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            } catch (e) {
                console.error('Modal open error:', e);
                closeModal(); // Гарантированно закрываем при ошибке
            }
        }

        function closeModal() {
            try {
                modal.classList.remove('active');
            } finally {
                // ВАЖНО: всегда возвращаем скролл, даже если была ошибка
                document.body.style.overflow = '';
            }
        }

        // Навешиваем обработчики на карточки
        document.querySelectorAll('.dish-clickable').forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault(); // Блокируем любые стандартные действия
                openModal(card);
            });
        });

        // Закрытие по крестику
        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closeModal();
            });
        }
        
        // Закрытие по клику на фон
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
        
        // Закрытие по Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                closeModal();
            }
        });
    }
});

function copyReferralCode() {
    const code = document.getElementById('referral-code').textContent;
    const toast = document.getElementById('copy-toast');

    navigator.clipboard.writeText(code).then(() => {
        showToast(toast);
    }).catch(() => {
        // Фолбэк для старых браузеров
        const textarea = document.createElement('textarea');
        textarea.value = code;
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        
        showToast(toast);
    });
}

function showToast(element) {
    element.classList.add('show');
    setTimeout(() => {
        element.classList.remove('show');
    }, 2000);
}

// === КЛИК ПО ПОПУЛЯРНЫМ БЛЮДАМ НА ГЛАВНОЙ ===
document.querySelectorAll('.menu-preview__item').forEach(item => {
    item.addEventListener('click', function() {
        const modal = document.getElementById('dish-modal');
        if (!modal) return;
        
        // Элементы модалки
        const mImgContainer = document.getElementById('modal-img-container');
        const mImg = document.getElementById('modal-img');
        const mCategory = document.getElementById('modal-category');
        const mTitle = document.getElementById('modal-title');
        const mDesc = document.getElementById('modal-desc');
        const mPrice = document.getElementById('modal-price');
        
        // Берем данные из кликнутого элемента
        const title = this.dataset.title || '';
        const desc = this.dataset.desc || '';
        const price = this.dataset.price || '';
        const category = this.dataset.category || '';
        const imgSrc = this.dataset.img || '';
        
        // Заполняем модалку
        mTitle.textContent = title;
        mDesc.textContent = desc;
        mPrice.textContent = price ? `${price} ₽` : '';
        mCategory.textContent = category;
        
        if (imgSrc) {
            mImg.src = imgSrc;
            mImgContainer.style.display = 'block';
        } else {
            mImgContainer.style.display = 'none';
        }
        
        // Показываем
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    });
});

// Скрываем кнопку "Наше меню" на главной
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.btn--outline, .btn--primary');
    buttons.forEach(btn => {
        if (btn.textContent.trim() === 'Наше меню' || 
            btn.textContent.trim() === 'Смотреть всё меню') {
            btn.style.display = 'none';
        }
    });
});