# MindScore — Mental Health Score Predictor

A Flask app that predicts a student's mental health score (0–10) from their
social media habits, lifestyle, and stress level, using a trained
scikit-learn Random Forest pipeline.

## Run it

```bash
python -m pip install -r requirements.txt
python main.py
```

Then open http://127.0.0.1:5000/

Flow: **Home → Your Information (form) → Results → Suggestions**

## How prediction works

1. `templates/formpage.html` collects 12 inputs and POSTs them as JSON to
   `/predict`.
2. `main.py` builds a one-row DataFrame with the exact column names/order
   the model was trained on, groups the country into the same "top 11 +
   Other" buckets used during training, and runs it through
   `Mental_Health_Model.pkl`.
3. The API returns the score, a category (Excellent / Good / Fair / Needs
   Attention), a percentile (vs. the 5,000 students in the training CSV),
   a rough confidence score (based on agreement across the forest's trees),
   and a personalized list of suggestions based on which of the person's
   own habits look weakest.
4. `result.html` and `suggetion.html` read that JSON (passed via
   `sessionStorage`) and render the gauge, numbers, and suggestion cards
   dynamically — nothing on those pages is hardcoded anymore.


- `main.py` was empty — added the full Flask app + `/predict` API.
- The model was trained on **12 features including `Stress_Level`**, 


## Notes / limitations

- The training data only covers ages 18–24 — predictions for ages outside
  that range will extrapolate and may be less reliable.
- "Gender: Other" and any platform/purpose not seen in training (e.g. a
  platform outside the 12 the model knows) are handled gracefully by the
  model (they just get no signal from that feature) rather than causing
  an error, but obviously the model has no learned pattern for them.
- This is a data-driven estimate for a course/portfolio project, not a
  clinical assessment tool.
