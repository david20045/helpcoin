// web_app/script.js

const tg = window.Telegram.WebApp;

// Настройка стиля окна
tg.ready();

// Обработчик кнопки
document.getElementById('registerTask').addEventListener('click', () => {
    // Пример отправки данных обратно боту
    const data = {
        action: 'accept_task',
        task_id: 1 // Пример ID задачи
    };
    tg.sendData(JSON.stringify(data));
});