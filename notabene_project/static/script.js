document.addEventListener('DOMContentLoaded', () => {

    // Элементы основных экранов
    const mainScreen = document.getElementById('mainScreen');
    const chatScreen = document.getElementById('chatScreen');
    const chatsList = document.getElementById('chatsList');
    const createChatBtn = document.getElementById('createChatBtn');
    const backBtn = document.getElementById('backBtn');
    const chatCurrentTitle = document.getElementById('chatCurrentTitle');

    // Модалка создания чата
    const modalOverlay = document.getElementById('modalOverlay');
    const chatNameInput = document.getElementById('chatNameInput');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    const confirmModalBtn = document.getElementById('confirmModalBtn');

    // Окна настроек
    const openSettingsBtn = document.getElementById('openSettingsBtn');
    const settingsOverlay = document.getElementById('settingsOverlay');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const providersList = document.getElementById('providersList');
    const addNewProviderBtn = document.getElementById('addNewProviderBtn');

    // Форма провайдера
    const providerFormOverlay = document.getElementById('providerFormOverlay');
    const cancelProviderFormBtn = document.getElementById('cancelProviderFormBtn');
    const saveProviderFormBtn = document.getElementById('saveProviderFormBtn');
    const modelsFormList = document.getElementById('modelsFormList');
    const addModelLineBtn = document.getElementById('addModelLineBtn');

    // Поля ввода формы провайдера
    const provName = document.getElementById('provName');
    const provKey = document.getElementById('provKey');
    const provUrl = document.getElementById('provUrl');

    // Хранилище загруженных из БД провайдеров
    let localProviders = [];

    // --- ЛОГИКА ЧАТОВ ---
    function openChat(title) {
        chatCurrentTitle.textContent = title;
        chatScreen.classList.add('active');
        mainScreen.style.opacity = '0';
        mainScreen.style.transform = 'scale(0.98)';
    }

    function closeChat() {
        chatScreen.classList.remove('active');
        mainScreen.style.opacity = '1';
        mainScreen.style.transform = 'scale(1)';
    }

    function openModal() {
        chatNameInput.value = "";
        modalOverlay.classList.add('active');
        setTimeout(() => chatNameInput.focus(), 50);
    }

    function closeModal() {
        modalOverlay.classList.remove('active');
    }

    function submitNewChat() {
        let chatTitle = chatNameInput.value.trim();
        if (chatTitle === "") chatTitle = "Безымянный блокнот";

        const newChatItem = document.createElement('div');
        newChatItem.className = 'chat-item';
        newChatItem.dataset.chatTitle = chatTitle;
        newChatItem.innerHTML = `
            <div class="chat-info">
                <span class="chat-title">${chatTitle}</span>
                <span class="chat-date">Только что</span>
            </div>
            <div class="arrow-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </div>
        `;
        chatsList.insertBefore(newChatItem, chatsList.firstChild);
        closeModal();
        openChat(chatTitle);
    }

    // --- ЛОГИКА ОКНА НАСТРОЕК И API ---

    // Загрузка провайдеров из SQLite бэкенда
    async function loadProvidersFromDB() {
        try {
            const response = await fetch('/api/providers');
            localProviders = await response.json();
            renderProvidersList();
        } catch (err) {
            console.error("Ошибка загрузки провайдеров из БД:", err);
        }
    }

    // Отрисовка карточек провайдеров в окне настроек
    function renderProvidersList() {
        providersList.innerHTML = "";
        if (localProviders.length === 0) {
            providersList.innerHTML = `<div style="color: var(--text-muted); font-size: 0.9rem; text-align: center; padding: 10px;">Нет подключенных провайдеров</div>`;
            return;
        }

        localProviders.forEach(p => {
            const card = document.createElement('div');
            card.className = 'provider-card';
            card.innerHTML = `
                <div class="provider-card-info">
                    <h4>${p.name}</h4>
                    <span>Моделей: ${p.models ? p.models.length : 0}</span>
                </div>
                <div class="arrow-icon">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                </div>
            `;
            // При клике на карточку — открываем форму для редактирования
            card.addEventListener('click', () => openProviderForm(p));
            providersList.appendChild(card);
        });
    }

    // Динамическое добавление строки модели в форму ввода
    function addModelInputRow(name = "", code = "") {
        const row = document.createElement('div');
        row.className = 'model-row';
        row.innerHTML = `
            <input type="text" class="modal-input model-name-input" placeholder="Имя (напр. GPT-4o)" value="${name}">
            <input type="text" class="modal-input model-code-input" placeholder="Код (напр. gpt-4o)" value="${code}">
            <button type="button" class="remove-model-btn">&times;</button>
        `;

        row.querySelector('.remove-model-btn').addEventListener('click', () => row.remove());
        modelsFormList.appendChild(row);
    }

    // Открытие формы добавления/редактирования провайдера
    function openProviderForm(provider = null) {
        modelsFormList.innerHTML = "";

        if (provider) {
            document.getElementById('providerFormTitle').textContent = "Редактировать провайдера";
            provName.value = provider.name;
            provName.disabled = true; // Запретим менять имя (оно уникальный ключ в нашей БД)
            provKey.value = provider.api_key || "";
            provUrl.value = provider.base_url || "";
            if (provider.models) {
                provider.models.forEach(m => addModelInputRow(m.name, m.model_code));
            }
        } else {
            document.getElementById('providerFormTitle').textContent = "Новый провайдер";
            provName.value = "";
            provName.disabled = false;
            provKey.value = "";
            provUrl.value = "";
            addModelInputRow(); // Добавим одну пустую строчку для удобства
        }

        providerFormOverlay.classList.add('active');
    }

    // Сохранение провайдера и моделей в Базу Данных через API бэкенда
    async function handleSaveProvider() {
        const name = provName.value.trim();
        if (!name) return alert("Введите имя провайдера");

        // Собираем все строки моделей из формы
        const modelRows = modelsFormList.querySelectorAll('.model-row');
        const models = [];
        modelRows.forEach(row => {
            const mName = row.querySelector('.model-name-input').value.trim();
            const mCode = row.querySelector('.model-code-input').value.trim();
            if (mName && mCode) {
                models.push({ name: mName, model_code: mCode });
            }
        });

        const payload = {
            name: name,
            api_key: provKey.value.trim() || null,
            base_url: provUrl.value.trim() || null,
            models: models
        };

        try {
            const response = await fetch('/api/providers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                providerFormOverlay.classList.remove('active');
                loadProvidersFromDB(); // Обновляем список на экране настроек
            } else {
                const errData = await response.json();
                alert("Ошибка сохранения: " + errData.detail);
            }
        } catch (err) {
            alert("Не удалось отправить запрос к бэкенду.");
        }
    }

    // --- СЛУШАТЕЛИ СОБЫТИЙ ИНТЕРФЕЙСА ---
    createChatBtn.addEventListener('click', openModal);
    backBtn.addEventListener('click', closeChat);
    cancelModalBtn.addEventListener('click', closeModal);
    confirmModalBtn.addEventListener('click', submitNewChat);

    modalOverlay.addEventListener('click', (e) => { if (e.target === modalOverlay) closeModal(); });
    chatNameInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') submitNewChat(); if (e.key === 'Escape') closeModal(); });

    chatsList.addEventListener('click', (e) => {
        const clickedItem = e.target.closest('.chat-item');
        if (clickedItem) openChat(clickedItem.dataset.chatTitle);
    });

    // События Окна Настроек
    openSettingsBtn.addEventListener('click', () => {
        settingsOverlay.classList.add('active');
        loadProvidersFromDB(); // Сразу лезем в БД за списком
    });
    closeSettingsBtn.addEventListener('click', () => settingsOverlay.classList.remove('active'));
    settingsOverlay.addEventListener('click', (e) => { if (e.target === settingsOverlay) settingsOverlay.classList.remove('active'); });

    // События Формы Провайдеров
    addNewProviderBtn.addEventListener('click', () => openProviderForm(null));
    cancelProviderFormBtn.addEventListener('click', () => providerFormOverlay.classList.remove('active'));
    addModelLineBtn.addEventListener('click', () => addModelInputRow());
    saveProviderFormBtn.addEventListener('click', handleSaveProvider);
});