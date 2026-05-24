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
});
