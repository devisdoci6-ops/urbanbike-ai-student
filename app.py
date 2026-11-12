import argparse
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import pandas as pd
import joblib
from config.common import ROOT, REPORTS, FIGURES, FEATURES, read_splits

model_path = ROOT / "models" / "regression.joblib"
if not model_path.exists():
    raise SystemExit("Fillimisht ekzekuto: python run_all.py")

bundle = joblib.load(model_path)
summary = json.loads((REPORTS / "results_summary.json").read_text())
train, valid, test = read_splits()
dates = test.date.dt.strftime("%Y-%m-%d").tolist()


def predict(date):
    if date not in dates:
        raise ValueError("Zgjidh nje date nga lista e testit.")
    row = test.loc[test.date == pd.Timestamp(date)]
    model = bundle["models"][bundle["selected"]]
    value = float(max(0, model.predict(row[FEATURES])[0]))
    actual = int(row.iloc[0].rentals)
    return {"date": date, "model": bundle["selected"],
            "prediction": value, "actual": actual,
            "absolute_error": abs(value - actual)}


def page(result):
    options = []
    for date in dates:
        chosen = " selected" if date == result["date"] else ""
        options.append(f"<option{chosen}>{date}</option>")
    scores = pd.DataFrame(summary["metrics"])
    scores = scores.loc[scores.split == "test"].copy()
    scores = scores.rename(columns={
        "MAE": "Mean Absolute Error",
        "RMSE": "Root Mean Squared Error",
        "R2": "R² Score"
    })
    cols = ["model", "Mean Absolute Error", "Root Mean Squared Error",
            "R² Score"]
    table = scores[cols].to_html(
        index=False, float_format=lambda x: f"{x:.3f}",
        classes="metrics-table"
    )
    error_pct = (result['absolute_error'] / max(result['actual'], 1)) * 100
    return f'''<!doctype html>
<html lang="sq">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>UrbanBike AI</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{
  font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
  background:#eef2f7;color:#1a2332;line-height:1.6
}}
.hero{{
  background:linear-gradient(135deg,#0f2027 0%,#203a43 50%,#2c5364 100%);
  color:#fff;padding:48px 24px 36px;text-align:center
}}
.hero h1{{font-size:2.2rem;font-weight:700;letter-spacing:-0.5px;margin-bottom:6px}}
.hero .subtitle{{opacity:0.8;font-size:1rem}}
.hero .bike-icon{{font-size:2.8rem;margin-bottom:12px}}
.container{{max-width:960px;margin:0 auto;padding:24px 20px 48px}}
.form-card{{
  background:#fff;border-radius:14px;padding:28px 32px;
  box-shadow:0 2px 12px rgba(0,0,0,0.06);margin:-30px auto 28px;
  max-width:520px;text-align:center;position:relative;z-index:2
}}
.form-card label{{font-weight:600;font-size:1rem;color:#374151;margin-right:10px}}
.form-card select{{
  padding:10px 16px;border:2px solid #d1d9e6;border-radius:8px;
  font-size:1rem;background:#f8fafc;cursor:pointer;
  transition:border-color 0.2s
}}
.form-card select:focus{{border-color:#2c5364;outline:none}}
.form-card button{{
  padding:10px 28px;background:linear-gradient(135deg,#2c5364,#203a43);
  color:#fff;border:none;border-radius:8px;font-size:1rem;
  font-weight:600;cursor:pointer;margin-left:10px;
  transition:transform 0.15s,box-shadow 0.15s
}}
.form-card button:hover{{transform:translateY(-1px);box-shadow:0 4px 14px rgba(44,83,100,0.35)}}
.stats-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:28px}}
.stat-card{{
  background:#fff;border-radius:12px;padding:22px 24px;
  box-shadow:0 2px 10px rgba(0,0,0,0.05);text-align:center
}}
.stat-card .label{{font-size:0.82rem;text-transform:uppercase;letter-spacing:0.5px;color:#6b7a8d;margin-bottom:6px}}
.stat-card .value{{font-size:1.8rem;font-weight:700}}
.stat-card .value.primary{{color:#2c5364}}
.stat-card .value.success{{color:#059669}}
.stat-card .value.warning{{color:#d97706}}
.stat-card .unit{{font-size:0.85rem;color:#6b7a8d;margin-top:2px}}
.section{{
  background:#fff;border-radius:14px;padding:28px 32px;
  box-shadow:0 2px 12px rgba(0,0,0,0.06);margin-bottom:24px
}}
.section h2{{
  font-size:1.25rem;font-weight:700;color:#1a2332;
  margin-bottom:18px;padding-bottom:10px;
  border-bottom:2px solid #e5e9f0
}}
.section h2 .badge{{
  display:inline-block;background:#e0f2fe;color:#0369a1;
  font-size:0.72rem;padding:3px 10px;border-radius:20px;
  margin-left:10px;vertical-align:middle;font-weight:600;
  letter-spacing:0.3px
}}
.metrics-table{{width:100%;border-collapse:separate;border-spacing:0;font-size:0.95rem}}
.metrics-table th{{
  background:#f1f5f9;padding:12px 16px;text-align:left;
  font-weight:600;color:#374151;border-bottom:2px solid #e2e8f0
}}
.metrics-table th:first-child{{border-radius:8px 0 0 0}}
.metrics-table th:last-child{{border-radius:0 8px 0 0}}
.metrics-table td{{padding:11px 16px;border-bottom:1px solid #f1f5f9}}
.metrics-table tr:hover td{{background:#f8fafc}}
.metrics-table tr:last-child td:first-child{{border-radius:0 0 0 8px}}
.metrics-table tr:last-child td:last-child{{border-radius:0 0 8px 0}}
.fig-grid{{display:grid;grid-template-columns:1fr;gap:20px}}
.fig-grid img{{width:100%;border-radius:10px;border:1px solid #e5e9f0}}
.fig-grid .caption{{font-size:0.85rem;color:#6b7a8d;text-align:center;margin-top:6px}}
.footer{{
  text-align:center;padding:24px;color:#8896a4;font-size:0.85rem;
  border-top:1px solid #e5e9f0;margin-top:12px
}}
.model-badge{{
  display:inline-block;background:linear-gradient(135deg,#2c5364,#203a43);
  color:#fff;padding:4px 14px;border-radius:20px;font-size:0.85rem;
  font-weight:600;vertical-align:middle
}}
</style>
</head>
<body>
<div class="hero">
  <div class="bike-icon">\U0001f6b2</div>
  <h1>UrbanBike AI</h1>
  <p class="subtitle">Washington D.C., 2011–2012 · Parashikim historik një ditë përpara</p>
</div>
<div class="container">
  <div class="form-card">
    <form>
      <label>Zgjidh datën:</label>
      <select name="date">{''.join(options)}</select>
      <button type="submit">\U0001f50d Parashiko</button>
    </form>
  </div>

  <div class="stats-row">
    <div class="stat-card">
      <div class="label">Qiratë e parashikuara</div>
      <div class="value primary">{result['prediction']:.2f}</div>
      <div class="unit">qira / ditë</div>
    </div>
    <div class="stat-card">
      <div class="label">Vlera reale</div>
      <div class="value success">{result['actual']}</div>
      <div class="unit">qira / ditë</div>
    </div>
    <div class="stat-card">
      <div class="label">Gabimi absolut</div>
      <div class="value warning">{result['absolute_error']:.2f}</div>
      <div class="unit">{error_pct:.1f}% gabim</div>
    </div>
  </div>

  <div class="section">
    <h2>{result['date']} <span class="model-badge">{result['model']}</span></h2>
    <p style="color:#6b7a8d;margin-top:-8px">Modeli i zgjedhur automatikisht nga Mean Absolute Error më i ulët në validation.</p>
  </div>

  <div class="section">
    <h2>Metrikat e Testit <span class="badge">TEST SPLIT</span></h2>
    {table}
  </div>

  <div class="section">
    <h2>Parashikimet vs. Vlerat Reale <span class="badge">TEST</span></h2>
    <div class="fig-grid">
      <img src="/figures/04_predictions.png" alt="Parashikime dhe vlera reale">
      <div class="caption">Krahasimi i parashikimeve të modelit me vlerat reale në periudhën e testit</div>
    </div>
  </div>

  <div class="section">
    <h2>Eksplorimi i të Dhënave <span class="badge">TRAIN ONLY</span></h2>
    <div class="fig-grid">
      <img src="/figures/01_demand.png" alt="Kërkesa historike">
      <div class="caption">Kërkesa ditore dhe mesatarja lëvizëse 7-ditore në periudhën train</div>
      <img src="/figures/02_workingday.png" alt="Ditët e punës vs fundjavet">
      <div class="caption">Mesatarja e qirave sipas tipit të ditës</div>
      <img src="/figures/03_weather.png" alt="Moti dhe kërkesa">
      <div class="caption">Temperatura (lag 7 ditë) vs. kërkesa për qira</div>
    </div>
  </div>

  <div class="section">
    <h2>Klasifikimi <span class="badge">DEMO</span></h2>
    <div class="fig-grid">
      <img src="/figures/05_confusion.png" alt="Matrica e konfuzionit">
      <div class="caption">Matrica e konfuzionit — LogisticRegression, pragu = mediana e train</div>
    </div>
  </div>

  <div class="footer">
    <p>UrbanBike AI · Projekt grupi: Devis Doci, Linor Beqiri, Ergi Kazazi</p>
    <p style="margin-top:4px">Moti përdor lag7. Numërimet e djeshme supozohen të njohura. Ky demonstrim nuk verifikon parashikim të drejtpërdrejtë për sot.</p>
  </div>
</div>
</body>
</html>'''


class Handler(BaseHTTPRequestHandler):
    def send(self, body, kind, status=200):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.end_headers()
        self.wfile.write(body if isinstance(body, bytes) else body.encode())

    def do_GET(self):
        url = urlparse(self.path)
        if url.path.startswith("/figures/"):
            path = FIGURES / Path(url.path).name
            if path.suffix == ".png" and path.is_file():
                return self.send(path.read_bytes(), "image/png")
        if url.path not in ["/", "/api/predict"]:
            return self.send("Nuk u gjet.", "text/plain", 404)
        date = parse_qs(url.query).get("date", [dates[0]])[0]
        try:
            result = predict(date)
        except ValueError as error:
            return self.send(str(error), "text/plain; charset=utf-8", 400)
        if url.path == "/api/predict":
            return self.send(json.dumps(result), "application/json")
        self.send(page(result), "text/html; charset=utf-8")

    def log_message(self, *args):
        pass


parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args()
server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
print(f"Hap http://127.0.0.1:{args.port} . Ndalimi: Ctrl+C", flush=True)

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("Aplikacioni u ndal.")
finally:
    server.server_close()
