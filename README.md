# toonja.cz

Osobní web Marka Turnhöfera. Čisté statické HTML + jeden CSS soubor. Žádný framework, žádný build, žádné `npm install`, takže tu není nic, co by se mohlo rozbít.

## Struktura

```
index.html                 /                 (úvod)
o-mne.html                 /o-mne
spoluprace.html            /spoluprace
contact.html               /contact
blog/index.html            /blog/
blog/<slug>.html           /blog/<slug>       (články)
blog-kategorie/<x>.html    /blog-kategorie/<x>
404.html                   chybová stránka
sitemap.xml, robots.txt
assets/css/style.css       veškerý vzhled
assets/img/                všechny obrázky (nezávislé na Webflow CDN)
serve.py                   lokální náhled
```

URL adresy odpovídají původnímu webu na Webflow, takže SEO zůstane zachované.

## Náhled na počítači

```
python3 serve.py
```

Pak otevřete http://localhost:8000.

## Úpravy

- **Text:** otevřete příslušný `.html` soubor a přepište text. Jde to i přímo na GitHubu (ikona tužky).
- **Nový článek:** zkopírujte `blog/seo-copywriting.html` pod novým názvem, upravte nadpis, datum a text. Pak přidejte jeho kartu do `blog/index.html`, do příslušné kategorie v `blog-kategorie/` a jeho adresu do `sitemap.xml`.
- **Navigace a patička** jsou v každém HTML souboru stejné. Při změně je upravte ve všech (nebo o to požádejte Claude).

## Nasazení (doporučeno: GitHub Pages)

1. Na GitHubu: **Settings → Pages → Source: Deploy from a branch**, branch `main`, složka `/ (root)`.
2. Web poběží na `https://<účet>.github.io/toonja.cz/`. Pro vlastní doménu zadejte `www.toonja.cz` do **Custom domain** a u registrátora nastavte CNAME `www` → `<účet>.github.io`.
3. Každý push do `main` web automaticky aktualizuje.

Funguje to stejně i na Netlify nebo Cloudflare Pages (stačí připojit repozitář, bez build příkazu, výstupní složka `/`).

## Co bylo z původního webu vynecháno záměrně

- Ukázkové kurzy ze šablony (`/product/...`) a nepoužívané e-shopové stránky (`/checkout`, `/paypal-checkout`, `/order-confirmation`, `/search`). Nyní vrací 404.
- Zástupné texty ze šablony („350+ Expert teachers“, „Rated 5 out of 5…“ apod.) nahradila skutečná čísla ze stránky O mně.
- Kontaktní formulář (bez Webflow by nefungoval). Místo něj jsou přímé odkazy na e-mail, telefon a LinkedIn.
- Opravená patička: odkazy vedou tam, kam mají.
