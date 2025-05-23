// static/admin/js/taggit_script.js

// Используем django.jQuery(document).ready() для гарантии выполнения после загрузки DOM и jQuery
django.jQuery(document).ready(function($) { // Здесь $ будет локальным псевдонимом для django.jQuery
    const keywordsInput = $('#id_search_keywords'); // Исходное поле ввода, используем #id_search_keywords
    const keywordsContainer = $('<div class="tag-input-container"></div>'); // Контейнер для тегов и нового поля
    const newTextInput = $('<input type="text" placeholder="Добавить ключевое слово..." />'); // Новое поле для ввода тегов

    // Убедимся, что исходное поле существует
    if (!keywordsInput.length) {
        console.warn("Поле #id_search_keywords не найдено. Возможно, неверный ID или поле скрыто.");
        return; // Выходим, если поле не найдено
    }

    keywordsInput.after(keywordsContainer);
    keywordsContainer.append(newTextInput);

    // Функция для добавления тега
    function addTag(text) {
        text = text.trim();
        if (text === "") return;

        // Преобразуем существующие теги в массив, отфильтровываем пустые
        let existingTags = keywordsInput.val().split(',').map(tag => tag.trim()).filter(tag => tag !== '');

        // Проверяем на дубликаты (без учета регистра)
        if (existingTags.some(tag => tag.toLowerCase() === text.toLowerCase())) {
            return; // Не добавлять дубликаты
        }

        const tagElement = $('<span class="tag"><span>' + text + '</span><span class="remove-tag">&times;</span></span>');
        tagElement.insertBefore(newTextInput);

        // Обновляем скрытое поле
        existingTags.push(text);
        keywordsInput.val(existingTags.join(', '));
    }

    // Загрузка существующих тегов из поля при загрузке страницы
    const initialKeywords = keywordsInput.val();
    if (initialKeywords) {
        initialKeywords.split(',').forEach(function(tag) {
            if (tag.trim() !== '') { // Дополнительная проверка на пустые теги
                addTag(tag.trim());
            }
        });
    }

    // Обработка ввода в новом поле
    newTextInput.on('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Предотвращаем отправку формы
            addTag($(this).val());
            $(this).val(''); // Очищаем поле ввода
        } else if (e.key === 'Backspace' && $(this).val() === '') {
            // Если Backspace на пустом поле, удаляем последний тег
            const lastTag = keywordsContainer.find('.tag').last();
            if (lastTag.length) {
                const tagTextToRemove = lastTag.find('span:first').text(); // Получаем текст тега
                lastTag.remove();
                let existingTags = keywordsInput.val().split(',').map(tag => tag.trim()).filter(tag => tag !== '');
                existingTags = existingTags.filter(tag => tag.toLowerCase() !== tagTextToRemove.toLowerCase()); // Удаляем тег из массива
                keywordsInput.val(existingTags.join(', '));
            }
        }
    });

    // Обработка нажатия на крестик для удаления тега
    keywordsContainer.on('click', '.remove-tag', function() {
        const tagText = $(this).prev('span').text();
        $(this).closest('.tag').remove();

        let existingTags = keywordsInput.val().split(',').map(tag => tag.trim()).filter(tag => tag !== '');
        existingTags = existingTags.filter(tag => tag.toLowerCase() !== tagText.toLowerCase()); // Удаляем тег из массива
        keywordsInput.val(existingTags.join(', '));
    });

    // Обработка вставки текста с запятыми
    newTextInput.on('paste', function(e) {
        const pastedText = (e.originalEvent || e).clipboardData.getData('text');
        if (pastedText.includes(',')) {
            e.preventDefault();
            pastedText.split(',').forEach(function(tag) {
                addTag(tag.trim());
            });
        }
    });

    // Добавляем фокус на поле ввода при клике на контейнер
    keywordsContainer.on('click', function() {
        newTextInput.focus();
    });
});