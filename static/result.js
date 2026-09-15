const ICONS = {
    sleep:    { icon: 'bi-moon',           bg: 'purple-bg', textClass: '' },
    stress:   { icon: 'bi-person-heart',   bg: 'blue-bg',   textClass: '' },
    activity: { icon: 'bi-person-walking', bg: 'green-bg',  textClass: 'green-text' },
    screen:   { icon: 'bi-phone',          bg: 'red-bg',    textClass: 'orange-text' },
    study:    { icon: 'bi-book',           bg: 'blue-bg',   textClass: '' },
    connect:  { icon: 'bi-people',         bg: 'red-bg',    textClass: 'orange-text' },
    fortune:  { icon: 'bi-stars',          bg: 'purple-bg', textClass: '' },
};

const TONE_COLORS = {
    great:   { number: '#1fa15f', gaugeStart: '#6b46f7', gaugeEnd: '#1fa15f' },
    good:    { number: '#27a765', gaugeStart: '#6b46f7', gaugeEnd: '#27a765' },
    fair:    { number: '#d98a1f', gaugeStart: '#6b46f7', gaugeEnd: '#d98a1f' },
    low:     { number: '#d64545', gaugeStart: '#6b46f7', gaugeEnd: '#d64545' },
    fortune: { number: '#7c3aed', gaugeStart: '#7c3aed', gaugeEnd: '#ec4899' },
};

const FORTUNE_ICONS = ['bi-emoji-laughing', 'bi-stars', 'bi-balloon-heart'];
const FORTUNE_BGS   = ['purple-bg', 'blue-bg', 'green-bg'];

(function () {
    const raw = sessionStorage.getItem('mindscore_result');
    if (!raw) {
        window.location.href = '/assessment';
        return;
    }

    const data = JSON.parse(raw);
    if (data.teased) {
        // Update page heading
        document.getElementById('resultHeading').textContent =
            '\uD83D\uDD2E A Message For You, ' + data.name + '!';

       
        const scoreEl = document.getElementById('scoreNumber');
        scoreEl.textContent = '\u2728';
        scoreEl.style.fontSize = '2.8rem';
        scoreEl.style.lineHeight = '1';
        scoreEl.style.color = '#7c3aed';

       
        document.querySelector('.score-denom').style.display = 'none';
        document.querySelector('.score-gauge').style.opacity = '0.15';
        document.querySelector('.score-gauge').style.pointerEvents = 'none';

        
        document.getElementById('scoreCategory').textContent = '\uD83C\uDF00 Fortune Result';
        document.getElementById('scoreMessage').innerHTML = data.message;

       
        document.getElementById('keepPill').style.display = 'none';
        document.querySelector('.metric-grid').style.display = 'none';

        
        document.querySelector('.suggestion-panel h3').textContent =
            '\uD83C\uDF89 The Stars Suggest\u2026';

        
        const grid = document.getElementById('suggestionGrid');
        grid.innerHTML = '';
        (data.suggestions || []).forEach(function (s, i) {
            const el = document.createElement('div');
            el.className = 'suggestion';
            el.innerHTML =
                '<div class="suggestion-icon ' + FORTUNE_BGS[i % FORTUNE_BGS.length] + '">' +
                    '<i class="bi ' + FORTUNE_ICONS[i % FORTUNE_ICONS.length] + '"></i>' +
                '</div>' +
                '<div><h4>' + s.title + '</h4><p>' + s.text + '</p></div>';
            grid.appendChild(el);
        });

        return;
    }

    
    document.getElementById('scoreNumber').textContent = data.score.toFixed(1);
    document.getElementById('scoreCategory').textContent = data.category;
    document.getElementById('scoreMessage').innerHTML = data.message;
    document.getElementById('categoryMetric').textContent = data.category;
    document.getElementById('percentileMetric').textContent = data.percentile + (
        data.percentile === 11 || (data.percentile % 10 === 1 && data.percentile !== 11) ? 'st' :
        (data.percentile % 10 === 2 && data.percentile !== 12) ? 'nd' :
        (data.percentile % 10 === 3 && data.percentile !== 13) ? 'rd' : 'th'
    );
    document.getElementById('confidenceMetric').textContent = data.confidence + '%';

    
    const ARC_LENGTH = Math.PI * 85;
    const filled = (data.score / 10) * ARC_LENGTH;
    document.getElementById('gaugeValuePath').style.strokeDasharray =
        filled.toFixed(1) + ' ' + ARC_LENGTH.toFixed(1);

    const colors = TONE_COLORS[data.tone] || TONE_COLORS.good;
    document.getElementById('scoreNumber').style.color = colors.number;
    document.getElementById('gaugeStopStart').setAttribute('stop-color', colors.gaugeStart);
    document.getElementById('gaugeStopEnd').setAttribute('stop-color', colors.gaugeEnd);

    const keepPill = document.getElementById('keepPill');
    if (data.name) {
        document.getElementById('resultHeading').textContent =
            'Hey ' + data.name + '! \u2014 Your Mental Health Score';
    }
    if (data.tone === 'low' || data.tone === 'fair') {
        keepPill.innerHTML = 'You can do this <i class="bi bi-heart-fill"></i>';
    }

    const grid = document.getElementById('suggestionGrid');
    grid.innerHTML = '';
    (data.suggestions || []).forEach(function (s) {
        const meta = ICONS[s.key] || ICONS.connect;
        const el = document.createElement('div');
        el.className = 'suggestion';
        el.innerHTML =
            '<div class="suggestion-icon ' + meta.bg + '"><i class="bi ' + meta.icon + '"></i></div>' +
            '<div><h4 class="' + meta.textClass + '">' + s.title + '</h4><p>' + s.text + '</p></div>';
        grid.appendChild(el);
    });
})();
