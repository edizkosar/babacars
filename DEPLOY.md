# BabaCars — Deploy Rehberi

Proje **GitHub + Render** (ücretsiz) ile canlıya alınır. Aşağıdaki adımları sırayla izle.

---

## 1) GitHub'a Yükle

Proje klasöründe (PowerShell):

```powershell
git init
git add .
git commit -m "BabaCars ilk sürüm"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/babacars.git
git push -u origin main
```

> ⚠️ `.env`, `db.sqlite3`, `venv/`, `media/` **gönderilmez** (`.gitignore`'da). `.env` içinde gerçek
> Gmail şifresi var — sakın commit etme. Doğrulamak için: `git status` çıktısında `.env` görünmemeli.

---

## 2) Render'da Deploy (Blueprint ile — en kolay)

1. [render.com](https://render.com) → GitHub ile giriş yap
2. **New +** → **Blueprint**
3. Repoyu seç → Render `render.yaml`'ı otomatik okur
4. **Apply** → şunları otomatik kurar:
   - Web servisi (gunicorn)
   - Ücretsiz **PostgreSQL** veritabanı
   - `SECRET_KEY` otomatik üretilir, `DEBUG=False`, HTTPS açık
5. 3-5 dakikada site yayında: `https://babacars-xxxx.onrender.com`

### E-posta (opsiyonel)
Doğrulama maillerinin gitmesi için Render panelinde **Environment** sekmesinden:
- `EMAIL_HOST_USER` = gmail adresin
- `EMAIL_HOST_PASSWORD` = 16 haneli uygulama şifresi

Boş bırakılırsa mailler log'a yazılır (site yine çalışır).

---

## 3) İlk Kurulum (deploy sonrası bir kez)

Render panelinde web servisinin **Shell** sekmesinden:

```bash
python manage.py createsuperuser   # yönetim paneli girişi için
python manage.py seed_data         # örnek ilan verisi (varsa)
```

---

## Alternatif: Manuel (Blueprint kullanmadan)

Render → **New Web Service** → repoyu bağla:
- **Build Command:** `bash build.sh`
- **Start Command:** `gunicorn babacars.wsgi:application`
- **Environment** sekmesine ekle:

| Anahtar | Değer |
|---------|-------|
| `SECRET_KEY` | uzun rastgele bir değer |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `siteniz.onrender.com` |
| `DATABASE_URL` | (Postgres oluşturup bağla) |
| `DATABASE_SSL` | `True` |

---

## Önemli Notlar

- **Ücretsiz Render** 15 dk hareketsizlikte uyur; ilk istek ~30 sn gecikir (normaldir).
- **Yüklenen fotoğraflar kalıcı değildir** — ücretsiz tier'da disk geçicidir, deploy'da silinir.
  Kalıcı medya için Cloudinary/S3 gerekir (sonradan eklenebilir).
- **SQLite yerine Postgres** otomatik kullanılır (Blueprint ile). Lokal geliştirmede SQLite kalır.
- Lokal çalıştırma değişmedi: `python manage.py runserver`.
