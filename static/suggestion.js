const FOCUS_META = {
    stress:   { icon: 'bi-brain',           cls: 'stress',   label: 'Stress Management' },
    sleep:    { icon: 'bi-moon',            cls: 'sleep',    label: 'Sleep Quality' },
    activity: { icon: 'bi-person-walking',  cls: 'activity', label: 'Physical Activity' },
    screen:   { icon: 'bi-phone',           cls: 'stress',   label: 'Screen Time' },
    study:    { icon: 'bi-book',            cls: 'activity', label: 'Study Routine' },
    connect:  { icon: 'bi-people',          cls: 'sleep',    label: 'Social Connection' },
    diet:     { icon: 'bi-egg-fried',       cls: 'activity', label: 'Diet & Nutrition' },
    social:   { icon: 'bi-chat-heart',      cls: 'sleep',    label: 'Social Wellbeing' },
};


const CARD_META = {
    sleep:    { icon: 'bi-moon',           color: 'blue',   textClass: '' },
    stress:   { icon: 'bi-person-heart',   color: 'purple', textClass: '' },
    activity: { icon: 'bi-person-walking', color: 'green',  textClass: 'green-text',  listClass: 'green-list' },
    screen:   { icon: 'bi-phone',          color: 'orange', textClass: 'orange-text', listClass: 'orange-list' },
    study:    { icon: 'bi-book',           color: 'blue',   textClass: '' },
    connect:  { icon: 'bi-people',         color: 'orange', textClass: 'orange-text', listClass: 'orange-list' },
    diet:     { icon: 'bi-egg-fried',      color: 'green',  textClass: 'green-text',  listClass: 'green-list' },
    social:   { icon: 'bi-chat-heart',     color: 'purple', textClass: '' },
    fortune:  { icon: 'bi-stars',          color: 'purple', textClass: '' },
};


const FORTUNE_CARD_ICONS   = ['bi-emoji-laughing', 'bi-stars', 'bi-balloon-heart'];
const FORTUNE_CARD_COLORS  = ['purple', 'blue', 'green'];

(function () {
    const raw = sessionStorage.getItem('mindscore_result');
    if (!raw) {
        window.location.href = '/assessment';
        return;
    }
    const data = JSON.parse(raw);
    const suggestions = data.suggestions || [];

    if (data.teased) {
   
        document.getElementById('suggGreeting').textContent =
            'The stars have spoken, ' + data.name + '! \uD83C\uDF1F';


        document.querySelector('.page-heading h1').textContent = '\uD83D\uDD2E Fortune Edition';


        document.querySelector('.summary-card').style.display = 'none';

        const sectionTitle = document.querySelector('.section-title');
        const banner = document.createElement('div');
        banner.className = 'bottom-message';
        banner.style.cssText = 'margin-bottom:1.5rem; border-radius:12px; padding:1.1rem 1.4rem;';
        banner.innerHTML =
            '<i class="bi bi-magic" style="font-size:1.4rem; color:#7c3aed;"></i>' +
            '<span style="color:#3d0099; font-weight:500;">' + data.message + '</span>';
        sectionTitle.parentNode.insertBefore(banner, sectionTitle);

        sectionTitle.textContent = '\uD83C\uDF89 Fortune Suggestions';

        const grid = document.getElementById('recommendGrid');
        grid.innerHTML = '';
        suggestions.forEach(function (s, i) {
            const article = document.createElement('article');
            article.className = 'recommend-card';
            const iconCls   = FORTUNE_CARD_ICONS[i % FORTUNE_CARD_ICONS.length];
            const colorCls  = FORTUNE_CARD_COLORS[i % FORTUNE_CARD_COLORS.length];
            article.innerHTML =
                '<div class="recommend-icon ' + colorCls + '">' +
                    '<i class="bi ' + iconCls + '"></i>' +
                '</div>' +
                '<div class="recommend-content">' +
                    '<h3>' + s.title + '</h3>' +
                    '<p>' + s.text + '</p>' +
                '</div>';
            grid.appendChild(article);
        });

        const resourcesTitle = document.querySelector('.resources-title');
        const resourceGrid   = document.querySelector('.resource-grid');
        if (resourcesTitle) resourcesTitle.style.display = 'none';
        if (resourceGrid)   resourceGrid.style.display   = 'none';

        document.querySelector('.bottom-message:last-of-type').innerHTML =
            '<i class="bi bi-stars"></i>' +
            '<span>You asked the oracle and the oracle delivered. Have an amazing day! \uD83C\uDF08</span>';

        return; 
    }

    if (data.name) {
        document.getElementById('suggGreeting').textContent =
            'Hi ' + data.name + '! Here are steps tailored just for you.';
    }

    document.getElementById('suggScore').textContent = data.score_pct;
    document.getElementById('suggCategoryPill').textContent = data.category;
    document.getElementById('suggQuote').innerHTML = data.message;

    const keys = suggestions.map(function (s) { return s.key; });
    const focusContainer = document.getElementById('focusItems');
    focusContainer.innerHTML = '';
    keys.filter(function (k) { return k !== 'connect'; }).slice(0, 3).forEach(function (key) {
        const meta = FOCUS_META[key];
        if (!meta) return;
        const el = document.createElement('div');
        el.className = 'focus-item';
        el.innerHTML =
            '<div class="focus-icon ' + meta.cls + '"><i class="bi ' + meta.icon + '"></i></div>' +
            '<span>' + meta.label + '</span>';
        focusContainer.appendChild(el);
    });

    const grid = document.getElementById('recommendGrid');
    grid.innerHTML = '';
    suggestions.forEach(function (s) {
        const meta = CARD_META[s.key] || CARD_META.connect;
        const article = document.createElement('article');
        article.className = 'recommend-card';
        article.dataset.key = s.key;
        article.innerHTML =
            '<div class="recommend-icon ' + meta.color + '">' +
                '<i class="bi ' + meta.icon + '"></i>' +
            '</div>' +
            '<div class="recommend-content">' +
                '<h3 class="' + meta.textClass + '">' + s.title + '</h3>' +
                '<p>' + s.text + '</p>' +
            '</div>';
        grid.appendChild(article);
    });
})();
