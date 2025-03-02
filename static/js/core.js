/**
 * Основные функции для работы с данными Git-статистики
 */

// Глобальные переменные
window.hiddenDevelopers = new Set();

/**
 * Инициализация глобальных переменных и обработчиков событий
 */
function initCore() {
    console.log('Git Developer Statistics Visualization initialized');
    
    // Проверяем наличие данных
    if (!window.gitAnalysisData) {
        console.error('Data not found!');
        document.getElementById('error-message').textContent = 'Ошибка: Данные не найдены!';
        document.getElementById('error-container').style.display = 'block';
        return false;
    }
    
    // Инициализируем набор скрытых разработчиков из метаданных
    if (window.gitAnalysisData.metadata && window.gitAnalysisData.metadata.excluded_developers) {
        window.hiddenDevelopers = new Set(window.gitAnalysisData.metadata.excluded_developers);
    }
    
    return true;
}

/**
 * Получение отфильтрованного списка разработчиков (исключая скрытых)
 * @param {Object} data - данные о разработчиках
 * @returns {Array} - отфильтрованный и отсортированный массив разработчиков
 */
function getFilteredDevelopers(data, sortBy = 'total_commits') {
    if (!data || !data.developers) return [];
    
    return Object.entries(data.developers)
        .filter(([devId, _]) => !window.hiddenDevelopers.has(devId))
        .sort((a, b) => {
            // Сортировка по указанному полю (по умолчанию - по количеству коммитов)
            if (sortBy === 'name') {
                return a[1].name.localeCompare(b[1].name);
            }
            return b[1][sortBy] - a[1][sortBy];
        });
}

/**
 * Получение отфильтрованного рейтинга полезности (исключая скрытых разработчиков)
 * @param {Object} data - данные о рейтинге полезности
 * @returns {Array} - отфильтрованный и отсортированный массив рейтинга
 */
function getFilteredUsefulnessRating(data) {
    if (!data || !data.usefulness_rating) return [];
    
    return Object.entries(data.usefulness_rating)
        .filter(([devId, _]) => !window.hiddenDevelopers.has(devId))
        .sort((a, b) => b[1].score - a[1].score);
}

/**
 * Обновление всех разделов отчета после изменения видимости разработчиков
 * @param {Object} data - данные Git-статистики
 */
function updateAllSections(data) {
    // Перерисовка графиков
    if (typeof redrawCharts === 'function') {
        redrawCharts(data);
    }
    
    // Обновление рейтинга полезности
    if (typeof updateUsefulnessRatingVisibility === 'function') {
        updateUsefulnessRatingVisibility(data);
    }
    
    // Обновление статистики разработчиков
    if (typeof updateDeveloperStatsVisibility === 'function') {
        updateDeveloperStatsVisibility(data);
    }
}