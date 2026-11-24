# The ORB

An astrology yes/no oracle. Visitors enter their Sun (plus Moon and Rising if they know them), ask a question, and The ORB answers **Yes / No / Maybe**, with a rare **Cosmic Anomaly**. It's built with Python (FastAPI) and a single-page frontend. **No AI is used anywhere.** Every answer comes from hash math, and every sentence is built from hand-written phrase lists.

## Project layout

```
app.py              FastAPI app (Vercel finds `app` here automatically)
public/index.html   The website (served from Vercel's CDN)
public/assets/      Logo, wordmark, tagline, favicon, link-preview image
orb/
  engine.py         The ORB's workflow: classify → match intent → roll → anomaly → words
  intents.py        Detects rephrasings and follow-ups so answers never change
  probability.py    Seeded 40/40/20 roll + 5% Cosmic Anomaly + natal weights
  text.py           The ORB's voice: hand-written phrase banks
  nickname.py       Unhinged horoscope nicknames (never repeat)
  zenith.py         Daily Zenith Do/Don't lines
  models.py         Request/response shapes
  signs.py          Elements and modalities
cli.py              Chat with The ORB in the terminal
tests/test_orb.py   Checks every rule in the spec (and that no AI library is present)
```

## Run it locally

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000. To use the terminal version, run `python cli.py`. To run the tests: `pip install pytest && python -m pytest -q`.

## Deploy for free on Vercel

Netlify can't run Python, so this site deploys to Vercel instead. The workflow is the same: push to GitHub and the site updates on its own.

1. Push this folder to a GitHub repo.
2. Go to vercel.com, sign in with GitHub, choose **Add New → Project**, and import the repo.
3. Keep every default setting and click **Deploy**.

Each push to `main` redeploys the site.

## How the rules are enforced

| Spec rule | How |
|---|---|
| 40% Yes / 40% No / 20% Maybe, 5% Cosmic Anomaly | The roll comes from a SHA-256 hash of the question's intent. Hashes are uniform, so the long-run split holds (checked by a test over 40,000 questions). |
| Answers never change | The same intent gives the same hash, which gives the same answer, for everyone, forever. |
| Rephrasings, emotional pushes, "should I still do it?" | `intents.py` strips filler and emotion words. If no new scenario words are left, the question is matched to the previous one. |
| A new time, activity, or goal gets a new roll | Different content words, or a different time word (today vs. tomorrow), make a new intent. |
| Natal weights | Fire Sun is more decisive (less Maybe). Water or Air Moon adds uncertainty (more Maybe). A Fixed Rising resists change (leans No on quit/move/switch questions). The shifts are a few points, so the overall balance holds. |
| Never repeat phrasing | The browser sends the last 15 replies, and the voice re-draws if an opener or full line would repeat. |
| Nicknames never repeat | A nickname is rejected if it shares two components with an earlier one. Three candidates are made and the most unusual is kept. |
| Daily Zenith is one-time only | Only the exact phrase "daily zenith" triggers it. It's never saved to memory and doesn't affect the odds. |

The server is stateless, which is how free serverless hosting works. Each visitor's chart and conversation memory are kept in their own browser (localStorage). The "Make the ORB forget me" link wipes them.

## Change the salt to reshuffle every answer

All answers come from the salt `the-orb-sees-all`. To give your site its own unique set of answers, set an `ORB_SALT` environment variable to any phrase. Do this before launch, because changing it later changes every answer.
