document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("app-list");

    // Загружаем сгенерированный файл data.json
    fetch("data.json")
        .then(response => {
            if (!response.ok) {
                throw new Error("Файл data.json не найден");
            }
            return response.json();
        })
        .then(data => {
            container.innerHTML = ""; // Очищаем текст "Загрузка..."

            if (data.length === 0) {
                container.innerHTML = "<p>Приложений пока нет.</p>";
                return;
            }

            data.forEach(app => {
                const card = document.createElement("div");
                card.className = "app-card";

                card.innerHTML = `
                    <h2>${app.title}</h2>
                    <p><strong>Версия:</strong> ${app.version}</p>
                    <a href="${app.forum_url}" target="_blank">Перейти в тему на 4PDA</a>
                `;

                container.appendChild(card);
            });
        })
        .catch(error => {
            console.error("Ошибка загрузки:", error);
            container.innerHTML = "<p>Ошибка при загрузке данных. Запустите парсер!</p>";
        });
});
