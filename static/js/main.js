/**
 * Основной файл инициализации приложения
 */

// Запускаем инициализацию при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('Git Developer Statistics Visualization starting...');
    
    // Инициализируем ядро
    if (!initCore()) {
        console.error('Core initialization failed!');
        return;
    }
    
    // Отображаем данные
    displayAllData(window.gitAnalysisData);
    
    console.log('Git Developer Statistics Visualization loaded successfully');
});

/**
 * Отображает все данные
 * @param {Object} data - все данные Git-статистики
 */
function displayAllData(data) {
    // Отображаем метаданные
    if (data.metadata) {
        displayMetadata(data.metadata);
    }
    
    // Добавляем информацию о весах параметров
    displayWeightsInfo(data);
    
    // Добавляем элементы управления видимостью разработчиков
    addDeveloperVisibilityControls(data);
    
    // Отображаем статистику команды
    if (data.team_stats) {
        displayTeamStats(data.team_stats);
    }
    
    // Отображаем рейтинг полезности
    if (data.usefulness_rating && data.developers) {
        displayUsefulnessRating(data.usefulness_rating, data.developers);
    }
    
    // Отображаем статистику разработчиков
    if (data.developers) {
        displayDeveloperStats(data.developers);
    }
    
    // Создаем графики
    createCommitChart(data);
    createImpactChart(data);
    createContributionTimeline(data);
}

/**
 * Обновляет отображение всех данных после изменения видимости разработчиков
 * @param {Object} data - все данные Git-статистики
 */
function updateAllData(data) {
    // Обновляем статистику команды
    updateTeamStats(data);
    
    // Обновляем рейтинг полезности
    if (data.usefulness_rating && data.developers) {
        updateUsefulnessRatingVisibility(data);
    }
    
    // Обновляем статистику разработчиков
    if (data.developers) {
        updateDeveloperStatsVisibility(data);
    }
    
    // Перерисовываем графики
    redrawCharts(data);
}