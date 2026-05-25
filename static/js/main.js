document.addEventListener('DOMContentLoaded', () => {
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

    if (!datePicker) {
        return;
    }

    const hiddenInput = datePicker.querySelector('input[name="date"]');
    const valueLabel = datePicker.querySelector('.date-picker__value');
    const monthLabel = datePicker.querySelector('[data-date-month]');
    const grid = datePicker.querySelector('[data-date-grid]');
    const prevButton = datePicker.querySelector('[data-date-prev]');
    const nextButton = datePicker.querySelector('[data-date-next]');

    const monthNames = [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
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
                if (button.disabled) {
                    return;
                }

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
        if (datePicker.open) {
            renderCalendar();
        }
    });

    prevButton.addEventListener('click', () => {
        if (prevButton.disabled) {
            return;
        }
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
});
