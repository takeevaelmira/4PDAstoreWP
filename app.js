document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("app-list");
    const modalOverlay = document.getElementById("modal-overlay");
    const modalClose = document.getElementById("modal-close");
    const modalTitle = document.getElementById("modal-title");
    const modalDescription = document.getElementById("modal-description");
    const modalComments = document.getElementById("modal-comments");
    const modalForumLink = document.getElementById("modal-forum-link");

    let catalogData = [];

    // Загрузка JSON-файла с данными
    fetch("data.json")
        .then(response => {
            if (!response.ok) {
                throw new Error("Файл data.json не найден или пуст");
            }
            return response.json();
        })
        .then(data => {
            catalogData = data;
            renderCatalog(catalogData);
        })
        .catch(error => {
            console.error("Ошибка загрузки:", error);
            container.innerHTML = `
                <div class="error-card">
                    <h3>Не удалось загрузить данные</h3>
                    <p>Убедитесь, что GitHub Actions успешно выполнил запуск parser.py и создал файл data.json.</p>
                </div>
            `;
        });

    // Отрисовка списка карточек
    function renderCatalog(items) {
        container.innerHTML = "";

        if (!items || items.length === 0) {
            container.innerHTML = "<p>Каталог пуст. Запустите парсер.</p>";
            return;
        }

        items.forEach(item => {
            const card = document.createElement("div");
            card.className = "app-card";

            card.innerHTML = `
                <div class="card-body">
                    <h2 class="card-title">${escapeHtml(item.title)}</h2>
                    <p class="card-preview">${escapeHtml(item.description.substring(0, 150))}...</p>
                </div>
                <div class="card-footer">
                    <button class="btn-open" data-id="${item.id}">Просмотреть тему</button>
                    <a href="${item.forum_url}" target="_blank" rel="noopener" class="link-external">На 4PDA ↗</a>
                </div>
            `;

            container.appendChild(card);
        });

        // Навешиваем событие клика на кнопки просмотра
        document.querySelectorAll(".btn-open").forEach(button => {
            button.addEventListener("click", (e) => {
                const topicId = e.target.getAttribute("data-id");
                openTopicModal(topicId);
            });
        });
    }

    // Открытие темы в модальном окне
    function openTopicModal(id) {
        const topic = catalogData.find(t => t.id === id);
        if (!topic) return;

        modalTitle.textContent = topic.title;
        modalForumLink.href = topic.forum_url;
        modalDescription.textContent = topic.description;

        // Рендеринг комментариев
        modalComments.innerHTML = "";
        if (topic.comments && topic.comments.length > 0) {
            topic.comments.forEach(commentText => {
                const commentDiv = document.createElement("div");
                commentDiv.className = "comment-item";
                commentDiv.textContent = commentText;
                modalComments.appendChild(commentDiv);
            });
        } else {
            modalComments.innerHTML = "<p class='empty-text'>Комментариев не найдено.</p>";
        }

        modalOverlay.classList.remove("hidden");
        document.body.style.overflow = "hidden"; // Блокировка прокрутки фона
    }

    // Закрытие модального окна
    function closeModal() {
        modalOverlay.classList.add("hidden");
        document.body.style.overflow = "";
    }

    modalClose.addEventListener("click", closeModal);
    modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) closeModal();
    });

    function escapeHtml(text) {
        return text
            ? text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            : "";
    }
});
