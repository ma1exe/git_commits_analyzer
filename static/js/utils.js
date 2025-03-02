/**
 * Вспомогательные утилиты для работы с данными и DOM
 */

/**
 * Округляет число до указанной точности
 * @param {number} num - число для округления
 * @param {number} precision - количество знаков после запятой
 * @returns {number} - округленное число
 */
function roundNumber(num, precision = 2) {
    return Math.round(num * Math.pow(10, precision)) / Math.pow(10, precision);
}

/**
 * Создаёт DOM-элемент с указанным тегом, атрибутами и содержимым
 * @param {string} tag - HTML тег
 * @param {Object} attrs - атрибуты элемента
 * @param {string|Node|Array} content - содержимое элемента
 * @returns {HTMLElement} - созданный элемент
 */
function createElement(tag, attrs = {}, content = null) {
    const element = document.createElement(tag);
    
    // Устанавливаем атрибуты
    for (const [attr, value] of Object.entries(attrs)) {
        if (attr === 'style' && typeof value === 'object') {
            Object.assign(element.style, value);
        } else {
            element.setAttribute(attr, value);
        }
    }
    
    // Добавляем содержимое
    if (content !== null) {
        if (Array.isArray(content)) {
            content.forEach(item => {
                if (typeof item === 'string') {
                    element.appendChild(document.createTextNode(item));
                } else if (item instanceof Node) {
                    element.appendChild(item);
                }
            });
        } else if (typeof content === 'string') {
            element.textContent = content;
        } else if (content instanceof Node) {
            element.appendChild(content);
        }
    }
    
    return element;
}

/**
 * Форматирует дату в локальный формат
 * @param {string} dateStr - строка с датой в формате ISO или YYYY-MM-DD
 * @returns {string} - отформатированная дата
 */
function formatDate(dateStr) {
    if (!dateStr) return '';
    
    // Если это уже отформатированная дата в формате DD.MM.YYYY
    if (/^\d{2}\.\d{2}\.\d{4}$/.test(dateStr)) {
        return dateStr;
    }
    
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('ru-RU');
    } catch (e) {
        console.error('Error formatting date:', e);
        return dateStr;
    }
}

/**
 * Вычисляет процент от числа
 * @param {number} value - значение
 * @param {number} total - общее количество
 * @returns {number} - процент (округленный)
 */
function calculatePercentage(value, total) {
    if (!total) return 0;
    return Math.round((value / total) * 100);
}

/**
 * Создаёт цветовую палитру для заданного количества элементов
 * @param {number} count - количество цветов
 * @returns {Array} - массив цветов в формате rgba
 */
function generateColorPalette(count) {
    const baseColors = [
        [54, 162, 235],   // синий
        [255, 99, 132],   // красный
        [75, 192, 192],   // бирюзовый
        [255, 159, 64],   // оранжевый
        [153, 102, 255],  // фиолетовый
        [255, 205, 86],   // желтый
        [201, 203, 207],  // серый
        [255, 99, 71],    // томатный
        [46, 139, 87],    // зеленый
        [106, 90, 205]    // фиолетово-синий
    ];
    
    // Если цветов достаточно, возвращаем из базового набора
    if (count <= baseColors.length) {
        return baseColors.slice(0, count).map(color => `rgba(${color[0]}, ${color[1]}, ${color[2]}, 0.7)`);
    }
    
    // Если нужно больше цветов, генерируем дополнительные
    const result = [...baseColors.map(color => `rgba(${color[0]}, ${color[1]}, ${color[2]}, 0.7)`)];
    
    for (let i = baseColors.length; i < count; i++) {
        const r = Math.floor(Math.random() * 200 + 55);
        const g = Math.floor(Math.random() * 200 + 55);
        const b = Math.floor(Math.random() * 200 + 55);
        result.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
    }
    
    return result;
}

/**
 * Преобразует цвет из rgba в rgb с указанным значением alpha
 * @param {string} rgbaColor - цвет в формате rgba
 * @param {number} alpha - новое значение прозрачности
 * @returns {string} - цвет в формате rgba с новым значением alpha
 */
function adjustColorAlpha(rgbaColor, alpha) {
    return rgbaColor.replace(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*[\d\.]+\)/, `rgba($1, $2, $3, ${alpha})`);
}