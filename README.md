# toonja.cz

Osobní web Marka Turnhöfera. Je to 1:1 kopie webu z Webflow (šablona eLearner X) hostovaná jako statické soubory. Skryté a nefunkční prvky šablony jsou odstraněné. Žádný build ani `npm install`.

## Struktura

```
index.html                 /                 (úvod)
o-mne.html                 /o-mne
spoluprace.html            /spoluprace
contact.html               /contact          (kontaktní formulář)
blog/index.html            /blog/
blog/<slug>.html           /blog/<slug>       (články + newsletter formulář)
blog-kategorie/<x>.html    /blog-kategorie/<x>
404.html                   chybová stránka
assets/css/                styl z Webflow (beze změn, jen cesty k souborům)
assets/js/                 jQuery + webflow.js (animace, menu, posuvník) + forms.js
assets/fonts/, images/     písma a obrázky, nezávislé na Webflow CDN
serve.py                   lokální náhled
```

Odkazy jsou relativní, takže web funguje na `corrivati.github.io/toonja.cz/` i na vlastní doméně.

## Formuláře

Kontaktní formulář i odběr novinek posílá `assets/js/forms.js` přes službu [FormSubmit](https://formsubmit.co) na `turnhofer.marek@gmail.com`.

**Po prvním odeslání** přijde na tento e-mail žádost o aktivaci od FormSubmit. Je potřeba ji jednou potvrdit, jinak zprávy nedorazí.

## Náhled na počítači

```
python3 serve.py
```

Pak otevřete http://localhost:8000.

## Úpravy

- **Text:** najděte ho v příslušném `.html` souboru a přepište. Jde to i přímo na GitHubu (ikona tužky).
- **Vzhled:** neměňte třídy (`class="..."`), na nich visí styly i animace z Webflow.
- **Navigace a patička** jsou v každém souboru zvlášť. Při změně je upravte všude (nebo o to požádejte Claude).

## Co bylo z Webflow verze odstraněno

- Skryté prvky šablony: vyhledávání, filtr kategorií kurzů, „Rated 5 out of 5…“, „350+ Expert teachers / 580+ courses“, sekce „Grow your career with eLearner“, lorem ipsum v článcích.
- Ukázkové kurzy (`/product/...`) a e-shopové stránky (`/checkout` apod.). Nyní vrací 404.
- „Powered by Webflow“.

Opraveno: odkazy v patičce, české texty místo anglických v boxech článků („O autorovi“, „Odebírejte novinky“, „Nejnovější články“), titulky a popisy stránek kategorií.

## Slovník pojmů

Rozcestník `/slovnik/` a stránky pojmů `/slovnik/<slug>`. Data v `slovnik/pojmy.json`, texty v `slovnik/_obsah/`, stránky generuje `python3 tools/slovnik.py build`. Kontrola prolinkování článků: `python3 tools/slovnik.py check`. Pravidla v `CLAUDE.md`.
