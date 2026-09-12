document.getElementById('mindScoreForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const form = e.target;
    const btn = document.getElementById('continueBtn');
    const errorBox = document.getElementById('formError');
    errorBox.style.display = 'none';

    const payload = {
        name: form.name.value,
        age: form.age.value,
        gender: form.gender.value,
        country: form.country.value,
        academic_level: form.academic_level.value,
        platform: form.platform.value,
        purpose: form.purpose.value,
        usage: form.usage.value,
        unlocks: form.unlocks.value,
        study_hours: form.study_hours.value,
        activity_hours: form.activity_hours.value,
        sleep_hours: form.sleep_hours.value,
        stress_level: form.stress_level.value,
    };

    btn.disabled = true;
    btn.querySelector('span').textContent = 'Analyzing...';

    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.error || 'Something went wrong. Please try again.');
        }

        // Stash the result (and the answers, for the suggestions page) so
        // the next pages can render them dynamically.
        sessionStorage.setItem('mindscore_result', JSON.stringify(data));
        sessionStorage.setItem('mindscore_inputs', JSON.stringify(payload));

        window.location.href = '/result';
    } catch (err) {
        errorBox.textContent = err.message;
        errorBox.style.display = 'block';
        btn.disabled = false;
        btn.querySelector('span').textContent = 'Continue';
    }
});
