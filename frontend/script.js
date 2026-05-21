const mainScreen = document.getElementById('mainScreen');
const chatScreen = document.getElementById('chatScreen');
const chatsList = document.getElementById('chatsList');
const createChatBtn = document.getElementById('createChatBtn');
const backBtn = document.getElementById('backBtn');
const chatCurrentTitle = document.getElementById('chatCurrentTitle');

// Элементы модального окна
const modalOverlay = document.getElementById('modalOverlay');
const chatNameInput = document.getElementById('chatNameInput');
const cancelModalBtn = document.getElementById('cancelModalBtn');
const confirmModalBtn = document.getElementById('confirmModalBtn');

// Функция перехода в чат
function openChat(title) {
    chatCurrentTitle.textContent = title;
    chatScreen.classList.add('active');
    mainScreen.style.opacity = '0';
    mainScreen.style.transform = 'scale(0.98)';
}

// Возврат на главную
function closeChat() {
    chatScreen.classList.remove('active');
    mainScreen.style.opacity = '1';
    mainScreen.style.transform = 'scale(1)';
}

// Управление модальным окном
function openModal() {
    chatNameInput.value = ""; // Очищаем поле при открытии
    modalOverlay.classList.add('active');
    // Небольшой хак, чтобы фокус сработал сразу после анимации появления
    setTimeout(() => chatNameInput.focus(), 50);
}

function closeModal() {
    modalOverlay.classList.remove('active');
}

// Создание нового чата из модального окна
function submitNewChat() {
    let chatTitle = chatNameInput.value.trim();
    
    if (chatTitle === "") {
        chatTitle = "Безымянный блокнот";
    }

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
    
    closeModal(); // Закрываем окно ввода
    openChat(chatTitle); // Сразу переходим в чат
}

// Слушатели событий интерфейса
createChatBtn.addEventListener('click', openModal);
backBtn.addEventListener('click', closeChat);

// Слушатели модального окна
cancelModalBtn.addEventListener('click', closeModal);
confirmModalBtn.addEventListener('click', submitNewChat);

// Закрытие модалки при клике на темную область вокруг окна
modalOverlay.addEventListener('click', (event) => {
    if (event.target === modalOverlay) closeModal();
});

// Добавляем поддержку клавиши Enter для подтверждения и Esc для закрытия
chatNameInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') submitNewChat();
    if (event.key === 'Escape') closeModal();
});

// Переход в существующий чат при клике по списку
chatsList.addEventListener('click', (event) => {
    const clickedItem = event.target.closest('.chat-item');
    if (clickedItem) {
        const title = clickedItem.dataset.chatTitle;
        openChat(title);
    }
});