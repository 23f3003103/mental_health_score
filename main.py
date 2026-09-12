"""
MindScore backend
------------------
Serves the site's pages and exposes a JSON prediction API (/predict) that
feeds live form data through the trained scikit-learn pipeline
(Mental_Health_Model.pkl) to produce a dynamic Mental Health Score.
"""

import os
import bisect
import random
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "Mental_Health_Model.pkl")
DATA_PATH = os.path.join(
    BASE_DIR, "Student Social Media And Mental Health Impact.csv"
)

app = Flask(__name__)

model = joblib.load(MODEL_PATH)

FEATURE_COLUMNS = [
    "Study_Hours",
    "Age",
    "Avg_Daily_Usage_Hours",
    "Daily_Unlocks",
    "Physical_Activity_Hours",
    "Sleep_Hours_Per_Night",
    "Stress_Level",
    "Gender",
    "Academic_Level",
    "Most_Used_Platform",
    "Purpose_Of_Use",
    "Grouped_country",
]


TOP_COUNTRIES = {
    "India", "USA", "Canada", "Australia", "UK",
    "Germany", "Mexico", "Turkey", "France", "Spain",
}

# ---------------------------------------------------------------------------
# Easter-egg config — names that bypass the real model entirely.
# Matched case-insensitively after stripping whitespace.
# ---------------------------------------------------------------------------
TEASE_NAMES = {"sindhuja", "nancy"}

FORTUNE_MESSAGES = [
    "After hearing your name, my model got confused… how can someone's mental health score be in negative? 💀😂",
    "Analysis complete! Your score is so unique that even my model needs therapy now. 😭😂",
    "Your mental health score has been calculated… Please don't blame the developer. I just report the damage. 🙂😂",
    "Warning ⚠️: Your results are outside the normal range. Apparently, being this dramatic is not in our training dataset. 😂",
    "Our AI analyzed your data and reached one conclusion: You need fewer overthinking sessions and more chill. 😭",
    "Mental Health Score: 37/100. Model's comment: 'Madam, thoda sukoon naam ki bhi cheez hoti hai.' 😭😂",
    "Your analysis is complete… but the model has requested a personal meeting with you to discuss these results. 💀",
    "Result detected: 7% overthinking, 90% drama, 3% 'I'm totally fine.' 😂",
    "After analyzing your answers, the AI has one question: 'Aap theek ho ya bas Instagram story ke liye theek ho?' 😭😂",
    "Your mental health score looks suspicious… maybe the model got distracted after seeing your name. 👀😂",
]

JOKE_SUGGESTIONS = [
   {
        "key": "chaos",
        "title": "⚠️ Mental Peace Not Found",
        "text": "Our model searched everywhere for your mental peace. Unfortunately, it returned 404."
    },

    {
        "key": "overthinking",
        "title": "🧠 Overthinking Detected",
        "text": "Your brain appears to have 47 tabs open. We recommend closing at least 46 of them."
    },

    {
        "key": "drama",
        "title": "🎭 Drama Level: Premium",
        "text": "Congratulations! Your drama levels are statistically higher than necessary for a normal Tuesday."
    },

    {
        "key": "warning",
        "title": "🚨 AI Warning",
        "text": "The model has detected an unusual amount of attitude. Please restart yourself and try again."
    },

    {
        "key": "confused",
        "title": "🤖 Model Confused",
        "text": "After analyzing your answers, even our AI said: 'Bro, mujhe bhi nahi samajh aa raha isko.'"
    },

    {
        "key": "peace",
        "title": "🕊️ Peace.exe Has Stopped Working",
        "text": "Your mental peace application has crashed unexpectedly. Overthinking.exe is still running in the background."
    },

    {
        "key": "special",
        "title": "✨ Very Special Case",
        "text": "We've analyzed thousands of people, but your results made the model ask for a coffee break."
    },

    {
        "key": "attitude",
        "title": "😌 Attitude Detected",
        "text": "Your attitude score is surprisingly high. Unfortunately, there is no known treatment for this condition."
    },

    {
        "key": "secret",
        "title": "🔐 Classified Result",
        "text": "Your results are classified for your own safety. Even you might not be emotionally prepared for them."
    },

    {
        "key": "final",
        "title": "💀 Final Verdict",
        "text": "The AI has officially given up. Please consult your friends for further diagnosis. Especially the one who made this website."
    }
]

try:
    _scores_df = pd.read_csv(DATA_PATH)
    SCORE_DISTRIBUTION = sorted(_scores_df["Mental_Health_Score"].tolist())
except Exception:
    SCORE_DISTRIBUTION = None


def group_country(country: str) -> str:
    """Reproduce the training-time country bucketing."""
    return country if country in TOP_COUNTRIES else "Other"


def percentile_for_score(score: float) -> int:
    """% of the reference dataset that scored at or below this score."""
    if not SCORE_DISTRIBUTION:
        return 50
    idx = bisect.bisect_right(SCORE_DISTRIBUTION, score)
    return round((idx / len(SCORE_DISTRIBUTION)) * 100)


def confidence_for_input(row_df: pd.DataFrame) -> int:
    """
    Rough 'model confidence' signal: how much the individual trees in the
    random forest agree with each other on this specific input. Low spread
    across trees -> higher confidence.
    """
    try:
        preprocessor = model.named_steps["preprocessor"]
        forest = model.named_steps["random forest"]
        X = preprocessor.transform(row_df)
        tree_preds = np.array([t.predict(X)[0] for t in forest.estimators_])
        spread = tree_preds.std()
        # Empirically, spread is usually well under ~1.5 on the 0-10 scale.
        confidence = 100 - (spread / 1.5) * 45
        return int(np.clip(confidence, 55, 98))
    except Exception:
        return 80


def categorize(score: float) -> dict:
    """Map a 0-10 score to a category label, color, and short message."""
    if score >= 8:
        return {
            "category": "Excellent",
            "tone": "great",
            "message": "You're thriving! Your habits are clearly supporting your wellbeing.",
        }
    if score >= 6.5:
        return {
            "category": "Good",
            "tone": "good",
            "message": "You are doing well! However, there is always room for improvement.",
        }
    if score >= 5:
        return {
            "category": "Fair",
            "tone": "fair",
            "message": "You're doing okay, but a few habits could use some attention.",
        }
    return {
        "category": "Needs Attention",
        "tone": "low",
        "message": "Your wellbeing could use some support — a few small changes can help a lot.",
    }


def build_suggestions(payload: dict) -> list:
    """
    Generate personalized, data-driven wellness suggestions.

    Rules enforced here:
    - Only fire a tip when that area is genuinely weak (checked against
      evidence-based thresholds).
    - Reference the person's actual numbers wherever helpful.
    - Use varied phrasing so no two tips read the same.
    - Cap output at 4 suggestions.
    - If nothing is weak, return one positive-reinforcement note and one
      growth-oriented nudge instead of inventing a problem.
    """
    import random
    suggestions = []

    sleep = payload.get("Sleep_Hours_Per_Night", 8)
    stress = payload.get("Stress_Level", "Low")
    activity = payload.get("Physical_Activity_Hours", 2)
    usage = payload.get("Avg_Daily_Usage_Hours", 0)
    study = payload.get("Study_Hours", 0)
    academic = payload.get("Academic_Level", "")
    platform = payload.get("Most_Used_Platform", "social media")
    unlocks = payload.get("Daily_Unlocks", 0)

    # --- SLEEP ---
    if sleep < 5:
        suggestions.append({
            "key": "sleep",
            "title": "Reclaim Your Rest",
            "text": (
                f"At {sleep:.1f} hours a night you're running on empty — "
                "try moving your bedtime 30 minutes earlier this week and see how "
                "much sharper you feel by Friday."
            ),
        })
    elif sleep < 6.5:
        suggestions.append({
            "key": "sleep",
            "title": "A Little More Sleep",
            "text": (
                f"You're currently getting around {sleep:.1f} hours, "
                "just a bit short of the 7-hour sweet spot for students. "
                "Winding down screens 20 minutes earlier could be the easiest fix."
            ),
        })

    # --- STRESS ---
    if stress == "Very High":
        suggestions.append({
            "key": "stress",
            "title": "Take a Breather",
            "text": (
                "Very high stress takes a real toll over time. "
                "A 4-7-8 breathing exercise (inhale 4 s, hold 7 s, exhale 8 s) "
                "done twice before bed can noticeably lower your baseline tension."
            ),
        })
    elif stress == "High":
        suggestions.append({
            "key": "stress",
            "title": "Ease the Pressure",
            "text": (
                "High stress often snowballs if left unchecked. "
                "Even a 10-minute walk outside — no headphones — lets your mind reset "
                "and stops the stress spiral before it starts."
            ),
        })

    # --- PHYSICAL ACTIVITY ---
    if activity == 0:
        suggestions.append({
            "key": "activity",
            "title": "Start Moving Today",
            "text": (
                "You haven't logged any physical activity yet — that's okay, "
                "everyone starts somewhere. A 15-minute walk after dinner is a "
                "painless first step that your body will thank you for."
            ),
        })
    elif activity < 1:
        suggestions.append({
            "key": "activity",
            "title": "Move a Little More",
            "text": (
                f"With only {activity:.1f} h of activity per day, adding a short "
                "20-minute jog or yoga session three times a week would cross the "
                "threshold that research links to better mood and sharper focus."
            ),
        })

    # --- SCREEN / SOCIAL MEDIA USAGE ---
    if usage > 8:
        suggestions.append({
            "key": "screen",
            "title": "Digital Detox Time",
            "text": (
                f"Spending {usage:.1f} hours a day on {platform} is a lot — "
                "try setting a daily app limit of 2 hours and notice how much "
                "free headspace that unlocks for things you actually enjoy."
            ),
        })
    elif usage > 6:
        suggestions.append({
            "key": "screen",
            "title": "Trim Screen Hours",
            "text": (
                f"Your {usage:.1f}-hour daily {platform} habit is creeping into "
                "time that could go toward sleep or winding down. "
                "Designating one phone-free hour before bed is a small change with "
                "outsized benefits."
            ),
        })
    # High unlock frequency is its own strain even with moderate total time
    elif unlocks > 80 and usage > 4:
        suggestions.append({
            "key": "screen",
            "title": "Break the Scroll Loop",
            "text": (
                f"You're unlocking your phone around {int(unlocks)} times a day — "
                "that constant context-switching fragments your attention. "
                "Turning on Do Not Disturb during study blocks can break the habit fast."
            ),
        })

    # --- STUDY HOURS ---
    if study < 1 and academic != "High School":
        suggestions.append({
            "key": "study",
            "title": "Build Your Study Habit",
            "text": (
                f"Logging under an hour of study time a day tends to pile pressure "
                "onto exam season. Blocking off even 45 minutes each morning — "
                "before opening any apps — builds momentum without feeling overwhelming."
            ),
        })
    elif study < 1.5 and academic not in ("High School", ""):
        suggestions.append({
            "key": "study",
            "title": "Steady Study Rhythm",
            "text": (
                f"At {study:.1f} h of daily study you're below the 1.5 h students "
                "typically need to stay ahead of coursework. "
                "Try the Pomodoro method — 25 minutes on, 5 minutes off — to make "
                "each session count."
            ),
        })

    # --- FALLBACK: everything looks healthy ---
    if not suggestions:
        suggestions.append({
            "key": "connect",
            "title": "Keep the Momentum",
            "text": (
                "Your habits look genuinely solid — that's worth celebrating! "
                "One way to keep growing is to share what's working with a friend; "
                "teaching others cements your own good routines."
            ),
        })
        suggestions.append({
            "key": "activity",
            "title": "Push One Step Further",
            "text": (
                "Since your fundamentals are in great shape, consider adding a "
                "short journaling habit — 5 minutes at the end of each day — to "
                "track patterns and spot any stress before it builds."
            ),
        })
        return suggestions

    # Always add a social-connection nudge if space allows and it wasn't already added.
    connect_keys = [s["key"] for s in suggestions]
    if "connect" not in connect_keys and len(suggestions) < 4:
        suggestions.append({
            "key": "connect",
            "title": "Reach Out to Someone",
            "text": (
                "Don't underestimate the power of a 10-minute catch-up with a "
                "friend or family member — social connection is one of the strongest "
                "buffers against burnout."
            ),
        })

    return suggestions[:4]


def parse_and_validate(data: dict):
    """Turn raw form JSON into the exact row the pipeline expects."""
    required = [
        "age", "gender", "country", "academic_level", "platform", "purpose",
        "usage", "unlocks", "study_hours", "activity_hours", "sleep_hours",
        "stress_level",
    ]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        raise ValueError(f"Missing field(s): {', '.join(missing)}")

    try:
        age = float(data["age"])
        usage = float(data["usage"])
        unlocks = float(data["unlocks"])
        study_hours = float(data["study_hours"])
        activity_hours = float(data["activity_hours"])
        sleep_hours = float(data["sleep_hours"])
    except (TypeError, ValueError):
        raise ValueError("Numeric fields must be valid numbers.")

    row = {
        "Study_Hours": study_hours,
        "Age": age,
        "Avg_Daily_Usage_Hours": usage,
        "Daily_Unlocks": unlocks,
        "Physical_Activity_Hours": activity_hours,
        "Sleep_Hours_Per_Night": sleep_hours,
        "Stress_Level": data["stress_level"],
        "Gender": data["gender"],
        "Academic_Level": data["academic_level"],
        "Most_Used_Platform": data["platform"],
        "Purpose_Of_Use": data["purpose"],
        "Grouped_country": group_country(data["country"]),
        # Optional — not used by the ML pipeline but surfaced in the API response.
        "_name": str(data.get("name", "")).strip(),
    }
    return row


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/assessment")
def assessment():
    return render_template("formpage.html")


@app.route("/result")
def result():
    return render_template("result.html")


@app.route("/suggestions")
def suggestions_page():
    return render_template("suggetion.html")


# ---------------------------------------------------------------------------
# Prediction API
# ---------------------------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    try:
        row = parse_and_validate(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # -----------------------------------------------------------------------
    # Easter egg: if the submitted name matches any entry in TEASE_NAMES,
    # skip the real model entirely and return a playful fortune response.
    # -----------------------------------------------------------------------
    submitted_name = row.get("_name", "")
    if submitted_name.lower() in TEASE_NAMES:
        return jsonify({
            "teased": True,
            "name": submitted_name,
            "category": "Fortune",
            "tone": "fortune",
            "message": random.choice(FORTUNE_MESSAGES),
            "suggestions": random.sample(JOKE_SUGGESTIONS, 4),
        })

    row_df = pd.DataFrame([row], columns=FEATURE_COLUMNS)

    try:
        raw_score = float(model.predict(row_df)[0])
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {e}"}), 500

    raw_score = float(np.clip(raw_score, 0, 10))
    info = categorize(raw_score)
    percentile = percentile_for_score(raw_score)
    confidence = confidence_for_input(row_df)
    suggestions = build_suggestions(row)

    return jsonify({
        "teased": False,
        "score": round(raw_score, 1),
        "score_pct": round(raw_score * 10),   # e.g. 7.2 -> 72 (used on /100 views)
        "category": info["category"],
        "tone": info["tone"],
        "message": info["message"],
        "percentile": percentile,
        "confidence": confidence,
        "suggestions": suggestions,
        "name": submitted_name,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
