// Упрощенный JavaScript для управления UI
// Вся бизнес-логика перенесена в HTMX

document.addEventListener('DOMContentLoaded', () => {
    // Элементы основных экранов
    const mainScreen = document.getElementById('mainScreen');
    const chatScreen = document.getElementById('chatScreen');
    const createChatBtn = document.getElementById('createChatBtn');
    const backBtn = document.getElementById('backBtn');
    const chatCurrentTitle = document.getElementById('chatCurrentTitle');

    // Модалки
    const modalOverlay = document.getElementById('modalOverlay');
    const settingsOverlay = document.getElementById('settingsOverlay');
    const providerFormOverlay = document.getElementById('providerFormOverlay');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const openSettingsBtn = document.getElementById('openSettingsBtn');

    // --- УТИЛИТЫ ---
    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
        }
    };

    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
        }
    };

    window.addModelInputRow = function(name = "", code = "") {
        const modelsList = document.getElementById('modelsFormList');
        if (!modelsList) return;
        
        const row = document.createElement('div');
        row.className = 'model-row';
        row.innerHTML = `
            <input type="text" class="modal-input model-name-input" name="model_names[]" placeholder="Имя (напр. GPT-4o)" value="${name}">
            <input type="text" class="modal-input model-code-input" name="model_codes[]" placeholder="Код (напр. gpt-4o)" value="${code}">
            <button type="button" class="remove-model-btn" onclick="this.parentElement.remove()">&times;</button>
        `;
        modelsList.appendChild(row);
    };

    // --- ЛОГИКА ЧАТОВ (UI только) ---
    window.openChat = function(title) {
        chatCurrentTitle.textContent = title;
        chatScreen.classList.add('active');
        mainScreen.style.opacity = '0';
        mainScreen.style.transform = 'scale(0.98)';
    };

    function closeChat() {
        chatScreen.classList.remove('active');
        mainScreen.style.opacity = '1';
        mainScreen.style.transform = 'scale(1)';
    }

    // --- СЛУШАТЕЛИ СОБЫТИЙ (только UI) ---
    
    // Открытие модалки создания чата
    if (createChatBtn) {
        createChatBtn.addEventListener('click', () => {
            openModal('modalOverlay');
            // Фокус на поле ввода
            const input = modalOverlay.querySelector('input[name="chat_name"]');
            if (input) {
                setTimeout(() => input.focus(), 50);
            }
        });
    }

    // Навигация назад из чата
    if (backBtn) {
        backBtn.addEventListener('click', closeChat);
    }

    // Закрытие модалки создания чата
    const cancelModalBtn = modalOverlay.querySelector('button.btn-secondary');
    if (cancelModalBtn) {
        cancelModalBtn.addEventListener('click', () => closeModal('modalOverlay'));
    }

    // Клик вне модалки для закрытия
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => { 
            if (e.target === modalOverlay) closeModal('modalOverlay'); 
        });
    }

    // Настройки: открытие
    if (openSettingsBtn) {
        openSettingsBtn.addEventListener('click', () => {
            openModal('settingsOverlay');
            // Загружаем провайдеров через HTMX
            htmx.trigger('#providersList', 'loadProviders');
        });
    }

    // Настройки: закрытие
    if (closeSettingsBtn) {
        closeSettingsBtn.addEventListener('click', () => closeModal('settingsOverlay'));
    }

    // Клик вне настроек для закрытия
    if (settingsOverlay) {
        settingsOverlay.addEventListener('click', (e) => { 
            if (e.target === settingsOverlay) closeModal('settingsOverlay'); 
        });
    }

    // Клик вне формы провайдера
    if (providerFormOverlay) {
        providerFormOverlay.addEventListener('click', (e) => { 
            if (e.target === providerFormOverlay) closeModal('providerFormOverlay'); 
        });
    }

    // Добавляем обработчик для HTMX после вставки контента
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        // Если загрузили форму провайдера, открываем модалку
        if (evt.detail.target.id === 'providerFormOverlay' && evt.detail.target.innerHTML.trim()) {
            openModal('providerFormOverlay');
        }
    });

    // --- HTMX ИНТЕРЦЕПТОРЫ ---
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        // Можно добавить индикатор загрузки если нужно
    });

    document.body.addEventListener('htmx:afterRequest', function(evt) {
        // Можно убрать индикатор загрузки
    });

    // --- ИНИЦИАЛИЗАЦИЯ ---
    
    // Добавляем обработчик для загрузки провайдеров
    if (providersList) {
        providersList.addEventListener('loadProviders', function() {
            htmx.ajax('GET', '/htmx/providers', {
                target: '#providersList',
                swap: 'innerHTML'
            });
        });
    }
});