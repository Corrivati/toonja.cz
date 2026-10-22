# toonja.cz: pravidla pro Clauda

Osobní web Marka Turnhöfera (Mára). Čisté HTML na GitHub Pages, žádný build na hostingu. Popis struktury je v `README.md`.

## Hlas a styl
Texty píšu za Máru jako osobní značku: kamarádský odborník, výsledek první, krátké úderné věty, vykání, žádné dlouhé pomlčky. Úplný playbook je v jeho druhém mozku (`work/playbooks/mara-voice.md` v repu Corrivati/cortex.exe).

## Slovník pojmů (/slovnik/)
- Registr pojmů: `slovnik/pojmy.json`. Text pojmu: `slovnik/_obsah/<slug>.html` (meta v komentáři nahoře, pak obsah).
- Stránky generuje `python3 tools/slovnik.py build`. Hlavičku a patičku bere z `blog/index.html`, takže po změně menu stačí build zopakovat.
- `build --navrh` je jen pro náhled. Do produkční větve commituj výstup bez `--navrh` (rozcestník ukáže jen hotové pojmy a aktualizuje sitemap).
- Nový pojem: záznam v `pojmy.json` (stav `navrh`), text v `_obsah/`, stav na `hotovo`, build, pak `check` a doplnit odkazy z článků.

### Šablona pojmu
1. **Krátká odpověď** (`.slovnik-definice`): 40 až 60 slov, první věta je definice „X je…“. Tohle čte Google i AI.
2. 2 až 4 sekce H2 s `id`: jednoduše / jak to funguje / z praxe (Márův vlastní příklad, povinně) / na co si dát pozor.
3. Box „Mára říká“: jeden osobní postřeh, ne hláška z playbooku.
4. 2 až 3 otázky FAQ v meta.
5. Odkazy: aspoň 1 článek blogu, 2 až 4 související pojmy, CTA na spolupráci nebo kontakt.
6. Rozsah 300 až 700 slov. Pod 300 slov a bez vlastní zkušenosti pojem nepublikovat.
7. SEO: title do 60 znaků „Pojem: co to je a …“, description 140 až 155 znaků, H1 „Co je …“.
8. Nikdy nekopírovat text z cizích slovníků. Inspirace ano, formulace vlastní.

## Pravidlo pro nové a upravované články (povinné)
Před odevzdáním každého článku:
1. Spusť `python3 tools/slovnik.py check` a pojmy, které skript najde, prolinkuj na `/slovnik/<slug>`:
   - jen první výskyt v textu, kde odkaz čte přirozeně (ne v nadpisu, ne v perexu, ne v CTA),
   - max 5 odkazů na slovník v jednom článku, přednost mají pojmy, které čtenář nemusí znát,
   - nikdy neodkazuj z článku na pojem, jehož stránka vede zpátky na ten samý článek jako hlavní zdroj, pokud to čtenáři nic nepřidá.
2. Spusť `check --vse` a podívej se, které pojmy ve stavu `navrh` článek používá. Pokud je pojem v článku klíčový, navrhni Márovi jeho napsání (přidej mu prioritu v `pojmy.json`).
3. Nový pojem, který v článku vysvětluješ a ve slovníku chybí: přidej ho do `pojmy.json` jako `navrh` a zmiň to v shrnutí.
4. Obráceně: u pojmů, které článek rozebírá do hloubky, přidej článek do pole `clanky` v `pojmy.json`, ať na něj stránka pojmu odkazuje.
5. Klíčová slova článku nesmí kanibalizovat pojem: slovník cílí na „co je X“, článek na „jak X“ a návody. Když článek vlastní definici (SEO copywriting, Webflow), pojem má stav `clanek` a rozcestník vede rovnou na článek.

## Před publikací
- Náhled: `python3 serve.py`, zkontrolovat desktop i mobil.
- `sitemap.xml`: nová stránka tam musí být (slovník řeší build).
- Publikuje se z větve `claude/jolly-lovelace-gtqqia`. Návrhy dělej v samostatné větvi.
