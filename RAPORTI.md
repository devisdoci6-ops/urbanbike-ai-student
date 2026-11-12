# Raporti i studentit: UrbanBike AI

Studenti: Devis Doci, Linor Beqiri, Ergi Kazazi
Grupi (nëse punohet në grup): Devis Doci, Linor Beqiri, Ergi Kazazi
Data: 2026-11-13
GitHub-i im: https://github.com/devisdoci6-ops/urbanbike-ai-student
Figma: https://www.figma.com/design/CRlitxgYBno7v2wAqIkN7k/UrbanBike-AI-%E2%80%93-Dashboard?node-id=0-1

## Qëllimi

Si grup, ne ndërtuam një aplikacion të thjeshtë me inteligjencë artificiale që parashikon kërkesën ditore për biçikleta me qira nga të dhëna reale historike të qirave dhe të motit. Kaluam të gjithë procesin: pastrimin e të dhënave, grafikët, modelet me Scikit-learn me ndarje train/validation/test, krahasimin e modeleve, klasifikimin, konceptin në Figma, kodin në VS Code dhe publikimin në GitHub.

Problemi që zgjidhim: Sa qira biçikletash priten për ditën pasuese në Washington, D.C.?
Target-i y: `rentals` (numri total i qirave ditore, kolona `cnt` në UCI).
Predictorët X: `rentals_lag1`, `rentals_lag7`, `rentals_mean7`, `temp_c_lag7`, `rain_mm_lag7`, `wind_ms_lag7`, `trend_days`, `weekday`, `month`, `workingday`, `holiday`.
Koha kur parashikojmë dhe çfarë informacioni është i njohur: Parashikojmë një ditë përpara. Supozojmë se dihen qiratë e ditës së djeshme dhe të ditëve të kaluara, si dhe kalendari i ditës (dita e javës, muaji, dita e punës, festa). Moti përdoret me vonesë 7-ditore (lag7), pra vetëm vlera që dihen përpara ditës së parashikimit.

## Pastrimi

Burimet reale dhe çelësi i bashkimit: Ne përdorëm UCI Bike Sharing (`data/raw/day.csv`, 731 ditë, 2011–2012) dhe NASA POWER (`data/raw/nasa_weather.csv`: `temp_c`, `rain_mm`, `wind_ms`). I bashkuam me çelësin `date`, një-me-një, dhe morëm 731 rreshta.
Dallimi mes origjinaleve dhe kopjes didaktike: Skedarët në `data/raw/` nuk u ndryshuan (UCI ka 731 rreshta dhe 0 mungesa). Gabimet u krijuan me kod vetëm në kopjen ushtrimore `data/teaching/dirty.csv`, që pastrimi të demonstrohet në mënyrë të kontrolluar.
Rreshtat para/pas: Kopja didaktike kishte 743 rreshta. Pas pastrimit mbetën 731 rreshta. Pas krijimit të lag-eve mbetën 724 rreshta për modelim.
Dublimet: Gjetëm dhe hoqëm 12 rreshta identikë.
Mungesat para/pas konvertimit: Para konvertimit kishte 30 qeliza bosh. Kolona `temp_c` ishte tekst (`object`) sepse përmbante 6 vlera tekstuale "gabim". Pas konvertimit në numër, këto u bënë NaN, pra gjithsej 36 mungesa meteorologjike. `date` u kthye në datetime dhe `temp_c` në float64. Të dhënat u renditën sipas datës.
Arsyeja e imputimit vetëm me train: Mungesat plotësohen me medianë brenda Pipeline-it, dhe mediana mësohet vetëm nga train. Kështu validation dhe testi nuk ndikojnë në trajnim (shmangim rrjedhjen e informacionit). Mungesa nuk trajtohet si 0 °C, sepse kjo do të ishte një vlerë e rreme.

## Grafikët

Vëzhgimi 1 dhe figura përkatëse (`reports/figures/01_demand.png`): Në periudhën train, qiratë ditore rriten nga rreth 1 000–2 000 në janar 2011 në rreth 4 500–5 000 në verën e 2011-s. Ato bien në dimrin 2011–2012 dhe rriten përsëri deri në rreth 6 000 në pranverën e 2012-s. Vihet re një prirje rritëse nga viti në vit, një model sezonal, si dhe luhatje të forta nga dita në ditë.
Vëzhgimi 2 dhe figura përkatëse (`reports/figures/03_weather.png`): Ditët me temperaturë më të lartë 7 ditë më parë kanë zakonisht më shumë qira. Pikat me temperaturë nën 0 °C janë kryesisht nën 3 000 qira, ndërsa mbi 20 °C shumica janë mes 3 500 dhe 5 500. Shpërndarja është e gjerë, prandaj temperatura vetëm nuk e shpjegon kërkesën. Sipas `02_workingday.png`, mesatarja në ditë pune (rreth 3 750) është pak më e lartë se në fundjavë/festë (rreth 3 570), por dallimi është i vogël.
Pse një lidhje e dukshme nuk provon shkakësi: Temperatura dhe qiratë rriten njëkohësisht me stinën dhe me rritjen e përdorimit të shërbimit në 2012. Një faktor i tretë (stina, muaji, rritja e qytetit) mund të shkaktojë të dyja. Grafiku tregon lidhje, jo shkak.

## Vlerësimi

| Modeli | Validation MAE | Test MAE | Test RMSE | Test R² |
|---|---:|---:|---:|---:|
| Yesterday | 775.203 | 916.402 | 1330.386 | 0.539 |
| DummyMean | 2953.866 | 2494.628 | 2790.064 | -1.027 |
| Ridge | 687.558 | 893.251 | 1252.655 | 0.591 |
| RandomForest | 1821.528 | 1671.499 | 2042.654 | -0.087 |

Ndarja kohore: Train 2011-01-08 – 2012-04-30 (479 ditë), Validation 2012-05-01 – 2012-08-31 (123), Test 2012-09-01 – 2012-12-31 (122).
Modeli i zgjedhur nga validation dhe arsyeja: Ne zgjodhëm Ridge, sepse ka MAE-në më të ulët në validation (687.558) mes dy kandidatëve ML. Zgjedhja u bë para se të shiheshin rezultatet e testit. Në test, Ridge mbetet më i miri (MAE 893.251, R² 0.591) dhe e kalon pak baseline-in Yesterday (916.402).
Rezultati i provës me Random Forest: Random Forest doli më keq në validation (MAE 1821.528) dhe në test (MAE 1671.499, R² −0.087). Një shpjegim i mundshëm është se pemët nuk mund të parashikojnë vlera më të larta se ato që kanë parë në train, ndërsa kërkesa në 2012 ishte më e lartë. Kjo tregon se një model më kompleks nuk është automatikisht më i mirë.
Interpretimi i gabimit në qira për ditë: Me Ridge, parashikimi gabon mesatarisht rreth 893 qira në ditë në periudhën e testit. RMSE (1252.655) është më i madh se MAE, gjë që tregon disa ditë me gabime të mëdha. Shembull nga aplikacioni: për 2012-09-01 parashikimi është 6834.73 qira, vlera reale 6140, gabimi absolut 694.73.
Rezultati i klasifikimit, nëse u realizua: Po. Pragu (mediana e train-it) është 3907 qira, dhe "kërkesë e lartë" do të thotë rentals ≥ 3907. Në test ka 103 ditë të larta dhe 19 normale. DummyMostFrequent ka accuracy 84.43%, por balanced accuracy 50.00% dhe macro-F1 0.458, sepse nuk dallon asnjë ditë normale. LogisticRegression ka accuracy 91.80%, balanced accuracy 77.98% dhe macro-F1 0.820, me matricë konfuzioni [[11, 8], [2, 101]]: 8 ditë normale u klasifikuan si të larta dhe 2 ditë të larta si normale. Accuracy vetëm është mashtruese kur klasat janë të pabalancuara.

## Kufizimet

1. Të dhënat mbulojnë vetëm një qytet (Washington, D.C.) dhe një periudhë historike (2011–2012). Rezultatet nuk vlejnë automatikisht për qytete ose vite të tjera.
2. Moti i NASA POWER vjen nga një rrjet meteorologjik me rezolucion të gjerë dhe në kohë LST, jo nga një stacion lokal. Përdorimi i lag7 nuk i zgjidh të gjitha kufizimet e këtyre të dhënave historike.
3. Parashikimi njëditor supozon se dihen qiratë e ditës së djeshme. Aplikacioni është demonstrim historik me datat e testit, jo shërbim i testuar për parashikimin e kërkesës së sotme.

## Kontributet individuale

| Studenti | Skedari/ekrani | Puna dhe vendimi | Commit/prova |
|---|---|---|---|
| Devis Doci | `.gitignore`, `requirements.txt`, `config/common.py`, `01_clean.py`, `app.py`, `run_all.py` | Përgatiti Git-in dhe mjedisin `.venv`; ndërtoi pastrimin (12 dublime, 36 mungesa, tipet) dhe vendosi që imputimi të mësohet vetëm nga train; ndërtoi aplikacionin lokal me etiketat e konceptit Figma dhe e publikoi projektin në GitHub | `reports/data_quality.json`; prova e aplikacionit për 2012-09-01: 6834.73 / 6140 / 694.73 |
| Linor Beqiri | `02_visualize.py`, Figma | Krijoi tre grafikët vetëm nga periudha train dhe shkroi vëzhgimet; projektoi konceptin e ndërfaqes 1440×900 me fushën e datës, butonin Parashiko dhe hapësirën e rezultatit | `reports/figures/01–03`; lidhja Figma në këtë raport |
| Ergi Kazazi | `03_train.py`, `04_classify.py` | Trajnoi dhe krahasoi Yesterday, DummyMean, Ridge dhe RandomForest; zgjodhi Ridge sipas MAE në validation; realizoi klasifikimin normale/e lartë dhe interpretoi pse accuracy vetëm është mashtruese | `reports/regression_metrics.csv`, `reports/classification_metrics.json` |

Të tre e kontrolluam projektin së bashku kundrejt udhëzimeve të lëndës dhe e shkruam raportin si grup.

## Burimet

UCI: https://doi.org/10.24432/C5W894
NASA: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
Provenienca lokale: data/raw/provenance.json
