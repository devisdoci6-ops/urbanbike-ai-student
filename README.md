# UrbanBike AI: Parashikimi i kërkesës ditore për biçikleta me qira

Projekt grupi për lëndën e Inteligjencës Artificiale.

| Anëtari i grupit | Roli kryesor |
|---|---|
| **Devis Doci** | Git/GitHub, konfigurimi, pastrimi i të dhënave, aplikacioni lokal |
| **Linor Beqiri** | Vizualizimi, interpretimi i grafikëve, koncepti në Figma |
| **Ergi Kazazi** | Modelet e regresionit dhe klasifikimit, vlerësimi dhe kufizimet |

- **Raporti i plotë:** [RAPORTI.md](RAPORTI.md)
- **Koncepti i ndërfaqes (Figma):** https://www.figma.com/design/CRlitxgYBno7v2wAqIkN7k/UrbanBike-AI-%E2%80%93-Dashboard?node-id=0-1
- **Repozitori:** https://github.com/devisdoci6-ops/urbanbike-ai-student

---

## 1. Çfarë kemi ndërtuar

Ne kemi ndërtuar një aplikacion të thjeshtë me inteligjencë artificiale që parashikon **sa biçikleta do të merren me qira ditën e nesërme në Washington, D.C.** Përdorëm të dhëna reale historike për qiratë (UCI Bike Sharing) dhe për motin (NASA POWER), për vitet 2011–2012.

Kemi kaluar të gjithë procesin, nga të dhënat reale deri te një parashikim që mund të vlerësohet:

1. **Kontrolli dhe pastrimi i të dhënave:** vlera që mungojnë, dublime dhe tipe të gabuara.
2. **Grafikë** për të kuptuar si ndryshon kërkesa.
3. **Modele me Scikit-learn**, me ndarje kohore në train, validation dhe test.
4. **Krahasimi i modeleve** me MAE, RMSE dhe R².
5. **Klasifikimi** i kërkesës në *normale* ose *të lartë* (demonstrim).
6. **Koncepti i ndërfaqes në Figma.**
7. **Aplikacioni lokal** në shfletues, që përdor modelin e trajnuar.
8. **Raporti** me rezultatet, kufizimet dhe kontributin e secilit.

**Pyetja e projektit:** Sa qira biçikletash priten për ditën pasuese në Washington, D.C.?
**Target-i (y):** `rentals`, numri total i qirave në ditë.

---

## 2. Të dhënat

| Burimi | Skedari | Përmbajtja |
|---|---|---|
| UCI Bike Sharing | `data/raw/day.csv` | 731 ditë (2011–2012), `cnt` = qiratë totale |
| NASA POWER | `data/raw/nasa_weather.csv` | `temp_c` (°C), `rain_mm` (mm/ditë), `wind_ms` (m/s) |
| NASA POWER (origjinal) | `data/raw/nasa_power_daily.json` | Përgjigjja origjinale JSON e NASA-s |
| Proveniencë | `data/raw/provenance.json`, `data/raw/SOURCES.md` | URL-të, hash-et dhe atribimi |

Dy burimet i kemi bashkuar sipas `date`. **Skedarët origjinalë në `data/raw/` nuk i kemi ndryshuar.** Për të demonstruar pastrimin, kodi krijon një kopje ushtrimore me gabime të kontrolluara (`data/teaching/dirty.csv`): 30 qeliza bosh, 6 vlera tekstuale "gabim" te temperatura dhe 12 rreshta të dubluar.

---

## 3. Struktura e projektit

```
urbanbike-ai-student/
├── .gitignore            # përjashton .venv/, models/, cache dhe .env
├── requirements.txt      # gjashtë bibliotekat me versione të fiksuara
├── config/
│   ├── __init__.py
│   └── common.py         # dosjet, kolonat, ndarjet kohore, funksione të përbashkëta
├── 01_clean.py           # bashkimi, kopja didaktike, pastrimi dhe lag-et
├── 02_visualize.py       # tre grafikë vetëm nga periudha train
├── 03_train.py           # modelet e regresionit dhe vlerësimi
├── 04_classify.py        # klasifikimi normale / e lartë (fakultativ)
├── app.py                # aplikacioni lokal: formular, rezultate, grafikë
├── run_all.py            # ekzekuton me radhë 01 → 04
├── data/
│   ├── raw/              # burimet origjinale (të paprekura)
│   ├── teaching/         # kopja didaktike me gabime të kontrolluara
│   └── processed/        # të dhënat e pastruara dhe gati për model
├── reports/
│   ├── data_quality.json, teaching_changes.json
│   ├── regression_metrics.csv, results_summary.json, test_predictions.csv
│   ├── classification_metrics.json
│   └── figures/          # 01_demand, 02_workingday, 03_weather, 04_predictions, 05_confusion
├── RAPORTI.md            # raporti ynë
└── README_FILLIMI.md     # udhëzimi fillestar i lëndës
```

`.venv/` dhe `models/` mbeten vetëm në laptop dhe nuk ngarkohen në GitHub. Modeli rikrijohet nga kodi.

---

## 4. Si ta ekzekutoni projektin

**Kërkesat:** Python 3.12 dhe Git. Udhëzimet janë për Windows PowerShell. Në macOS/Linux përdorni `.venv/bin/python` në vend të `.\.venv\Scripts\python.exe`.

```powershell
git clone https://github.com/devisdoci6-ops/urbanbike-ai-student.git
cd urbanbike-ai-student

py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check        # pritet: No broken requirements found.
```

**Ekzekutimi i fazave një nga një:**

```powershell
.\.venv\Scripts\python.exe 01_clean.py
.\.venv\Scripts\python.exe 02_visualize.py
.\.venv\Scripts\python.exe 03_train.py
.\.venv\Scripts\python.exe 04_classify.py
```

ose të gjitha me një komandë:

```powershell
.\.venv\Scripts\python.exe run_all.py
```

**Aplikacioni:**

```powershell
.\.venv\Scripts\python.exe app.py
```

Hapni **http://127.0.0.1:8000** në shfletues dhe ndaleni serverin me **Ctrl+C**.
Nëse porta 8000 është e zënë: `.\.venv\Scripts\python.exe app.py --port 8001`.

> `app.py` kërkon modelin `models/regression.joblib`. Prandaj, pas klonimit, ekzekutoni fillimisht `run_all.py`.

---

## 5. Metoda

### Pastrimi (`01_clean.py`)

| Kontrolli | Vlera |
|---|---|
| Origjinali UCI | 731 rreshta, 0 mungesa |
| Kopja didaktike | 743 rreshta |
| Dublime identike të hequra | 12 |
| Pas pastrimit | 731 rreshta |
| Mungesa meteorologjike pas konvertimit | 36 (30 bosh + 6 tekste) |
| Pas krijimit të lag-eve | 724 rreshta |

- `date` kthehet nga tekst në datetime, dhe `temp_c` nga tekst (`object`) në `float64`. Teksti i gabuar bëhet NaN.
- Mungesat **nuk** i trajtojmë si 0 °C. Ato plotësohen me medianë brenda `Pipeline`, dhe mediana mësohet **vetëm nga train**, që të shmangim rrjedhjen e informacionit.

### Predictorët (X)

`rentals_lag1`, `rentals_lag7`, `rentals_mean7`, `temp_c_lag7`, `rain_mm_lag7`, `wind_ms_lag7`, `trend_days`, `weekday`, `month`, `workingday`, `holiday`

Parashikojmë një ditë përpara. Qiratë e ditëve të kaluara supozohen të njohura, dhe moti përdoret me vonesë 7-ditore (lag7).

### Ndarja kohore

| Pjesa | Datat | Ditë | Roli |
|---|---|---:|---|
| Train | 2011-01-08 – 2012-04-30 | 479 | Mëson parametrat dhe imputimin |
| Validation | 2012-05-01 – 2012-08-31 | 123 | Zgjedh modelin |
| Test | 2012-09-01 – 2012-12-31 | 122 | Vlerësimi final |

Ndarja është kronologjike, pa përzierje, që e ardhmja të mos ndikojë te trajnimi.

### Modelet

- **Yesterday:** baseline, "nesër si dje".
- **DummyMean:** baseline, mesatarja e train-it.
- **Ridge:** regresion linear me regularizim.
- **RandomForest:** provë me model jo-linear.

---

## 6. Rezultatet

### Regresioni

| Modeli | Validation MAE | Test MAE | Test RMSE | Test R² |
|---|---:|---:|---:|---:|
| Yesterday | 775.203 | 916.402 | 1330.386 | 0.539 |
| DummyMean | 2953.866 | 2494.628 | 2790.064 | -1.027 |
| **Ridge** ✅ | **687.558** | **893.251** | **1252.655** | **0.591** |
| RandomForest | 1821.528 | 1671.499 | 2042.654 | -0.087 |

- **Modeli i zgjedhur: Ridge**, sepse ka MAE-në më të ulët në validation. Zgjedhjen e bëmë para se të shihnim testin.
- Në test, Ridge gabon mesatarisht **rreth 893 qira në ditë** dhe është më i mirë se baseline-i Yesterday.
- **Random Forest** doli më keq. Një shpjegim i mundshëm është se pemët nuk parashikojnë vlera më të larta se ato të train-it, ndërsa kërkesa u rrit në 2012. Një model më kompleks nuk është automatikisht më i mirë.

**Shembull nga aplikacioni (2012-09-01):** parashikimi 6834.73 qira, vlera reale 6140, gabimi absolut 694.73.

### Klasifikimi (fakultativ)

"Kërkesë e lartë" do të thotë `rentals ≥ 3907`, mediana e train-it. Testi ka 103 ditë të larta dhe 19 normale.

| Modeli | Accuracy | Balanced accuracy | Macro-F1 |
|---|---:|---:|---:|
| DummyMostFrequent | 84.43% | 50.00% | 0.458 |
| LogisticRegression | 91.80% | 77.98% | 0.820 |

Matrica e konfuzionit për LogisticRegression është `[[11, 8], [2, 101]]`. Baseline-i merr accuracy të lartë pa dalluar asnjë ditë normale, prandaj vetëm accuracy është mashtruese kur klasat janë të pabalancuara.

### Grafikët (vetëm nga train)

| Figura | Çfarë tregon |
|---|---|
| `reports/figures/01_demand.png` | Kërkesa rritet nga viti në vit, ka model sezonal dhe luhatje ditore |
| `reports/figures/02_workingday.png` | Mesatarja në ditë pune (~3761) është pak më e lartë se në fundjavë/festë (~3570) |
| `reports/figures/03_weather.png` | Temperatura më e lartë 7 ditë më parë lidhet me më shumë qira. Kjo është lidhje, jo shkakësi |
| `reports/figures/04_predictions.png` | Parashikimet e Ridge kundrejt vlerave reale në test |
| `reports/figures/05_confusion.png` | Matrica e konfuzionit e klasifikimit |

---

## 7. Aplikacioni dhe dizajni

Aplikacioni (`app.py`) përdor vetëm bibliotekën standarde të Python-it për serverin dhe modelin Ridge të ruajtur. Përdoruesi zgjedh një datë nga periudha e testit dhe shtyp **Parashiko**. Faqja tregon:

- **Qiratë e parashikuara**, **Vlerën reale** dhe **Gabimin absolut**
- modelin e përdorur dhe metrikat e testit
- grafikët e parashikimeve, të eksplorimit dhe të klasifikimit

Ka edhe një endpoint JSON: `http://127.0.0.1:8000/api/predict?date=2012-09-01`.

Ndërfaqen e projektuam fillimisht në **Figma** (frame desktop 1440×900): fusha e datës, butoni *Parashiko* dhe hapësira e rezultatit me tre etiketat. Aplikacioni ndjek këtë koncept.

---

## 8. Kufizimet

1. Vetëm një qytet (Washington, D.C.) dhe një periudhë historike (2011–2012).
2. Moti NASA POWER vjen nga një rrjet meteorologjik me rezolucion të gjerë dhe në kohë LST, jo nga një stacion lokal.
3. Parashikimi njëditor supozon se dihen qiratë e djeshme. Aplikacioni është demonstrim historik, jo shërbim i testuar për kërkesën e sotme.

---

## 9. Kontributi i grupit

| Anëtari | Skedarët / ekrani | Puna |
|---|---|---|
| Devis Doci | `.gitignore`, `requirements.txt`, `config/common.py`, `01_clean.py`, `app.py`, `run_all.py` | Përgatitja e Git-it dhe e mjedisit Python; pastrimi dhe kontrolli i cilësisë së të dhënave; aplikacioni lokal dhe prova e tij; publikimi në GitHub |
| Linor Beqiri | `02_visualize.py`, Figma | Grafikët nga periudha train dhe interpretimi i tyre; koncepti i ndërfaqes në Figma |
| Ergi Kazazi | `03_train.py`, `04_classify.py` | Trajnimi dhe krahasimi i modeleve; zgjedhja e Ridge nga validation; klasifikimi dhe kufizimet |

Të tre kemi kontrolluar rezultatet kundrejt udhëzimeve të lëndës dhe kemi shkruar së bashku raportin.

---

## 10. Burimet

- UCI Bike Sharing Dataset: https://doi.org/10.24432/C5W894
- NASA POWER Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- Provenienca lokale: `data/raw/provenance.json`

**Bibliotekat:** numpy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, matplotlib 3.10.8, joblib 1.5.3, scipy 1.17.0.
