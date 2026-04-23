# 🔑 راهنمای تنظیم TMDB Access Token در GitHub Secrets

برای اجرای این اسکریپت، نیاز دارید توکن API خود را از سایت TMDB بگیرید و در GitHub Secrets ذخیره کنید. این راهنما را گام به گام دنبال کنید.

---

## 📝 مرحله ۱: گرفتن توکن از TMDB

1. وارد سایت [TMDB](https://www.themoviedb.org) شوید
2. اگر حساب ندارید، یک حساب رایگان بسازید
3. بعد از ورود، روی **آواتار خود** (بالا سمت راست) کلیک کنید
4. از منوی باز شده، **Settings** را انتخاب کنید
5. از منوی سمت چپ، روی **API** کلیک کنید

   (لینک مستقیم: `https://www.themoviedb.org/settings/api`)

6. در بخش **Request an API Key**، گزینه **Developer** را انتخاب کنید
7. فرم درخواست را پر کنید (مقدار `Application URL` و `Application Summary` می‌تواند هر چیزی باشد، مثلاً `https://github.com/your-username`)
8. بعد از ثبت، یک **API Key (v3 auth)** به شما داده می‌شود
9. پایین همان صفحه، یک **API Read Access Token (v4)** نیز وجود دارد

> ⚠️ **مهم:** توکنی که ما نیاز داریم، **API Read Access Token (v4)** است.  
> شکلی شبیه این دارد: `eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOi...`

10. آن توکن را کپی کنید (از `eyJ` تا آخر)

---

## 🔐 مرحله ۲: ذخیره توکن در GitHub Secrets

1. به رپازیتوری Fork شده خود در GitHub بروید
2. روی تب **Settings** کلیک کنید (بالا سمت راست)
3. از منوی سمت چپ، **Secrets and variables** را باز کنید
4. روی **Actions** کلیک کنید
5. دکمه سبز رنگ **New repository secret** را بزنید
6. در فیلد **Name**، دقیقاً بنویسید: TMDB_ACCESS_TOKEN
7. در فیلد **Secret**، توکنی که از TMDB کپی کرده‌اید را paste کنید
8. روی دکمه **Add secret** کلیک کنید

---

## ✅ مرحله ۳: تست صحت تنظیمات

1. به تب **Actions** رپو بروید
2. روی **Run workflow** کلیک کنید
3. یک سال مثلاً `2020` وارد کنید
4. بزنید **Run workflow**
5. اگر اسکریپت بدون خطا اجرا شود، یعنی توکن درست تنظیم شده است

---

## ❌ خطاهای رایج و رفع آنها

| خطا | دلیل | راه‌حل |
|------|------|--------|
| `TMDB_ACCESS_TOKEN not found` | Secret ساخته نشده | مرحله ۲ را دوباره انجام دهید |
| `Invalid token` | توکن اشتباه یا منقضی شده | یک توکن جدید از TMDB بگیرید |
| `401 Unauthorized` | دسترسی توکن کافی نیست | مطمئن شوید توکن v4 را گرفته‌اید |
| `Rate limit exceeded` | درخواست بیش از حد | چند دقیقه صبر کنید و دوباره试试 |

---

## 🔄 تمدید توکن (در صورت نیاز)

توکن TMDB تاریخ انقضا دارد. اگر بعد از چند ماه اسکریپت خطای `401` یا `Invalid token` داد:

1. دوباره وارد TMDB شوید
2. بروید به **Settings → API**
3. یک توکن جدید بسازید یا قدیمی را Regenerate کنید
4. در GitHub، Secret قبلی را حذف و با توکن جدید جایگزین کنید

---

## 📌 خلاصه سریع

```bash
# نام Secret:
TMDB_ACCESS_TOKEN

# مقدار آن:
eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOi... (توکن شما)

# محل تنظیم:
GitHub Repo → Settings → Secrets and variables → Actions → New repository secret
```
بعد از تنظیم، می‌توانید سال‌های مختلف را اجرا کنید و پوسترها را دانلود نمایید.
