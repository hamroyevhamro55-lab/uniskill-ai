# UniSkill AI (MVP)

Talabaning kompetensiyalarini aniqlash, rivojlantirish va dalillar bilan tasdiqlash platformasi.
**Stack:** Next.js (frontend) · FastAPI (backend) · PostgreSQL (SQLite lokal) · Claude API (ixtiyoriy).

## Lokal ishga tushirish
```bash
# 1) Backend (http://localhost:8000, docs: /docs)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 2) Frontend (http://localhost:3000)
cd frontend
cp .env.example .env.local
npm install && npm run dev
```
Demo akkauntlar (parol `demo1234`): `student@demo.uz`, `uni@demo.uz`, `hr@demo.uz`.

Testlar: `cd backend && pytest`

## Server (bepul hosting): Render + Vercel
1. Kodni GitHub'ga yuklang (`git init && git add . && git commit && git push`).
2. **Render** → New → Blueprint → repo'ni tanlang (`render.yaml` o'qiladi). Backend va PostgreSQL yaratiladi.
   Muhit o'zgaruvchilari: `CORS_ORIGINS` (keyingi qadamda olinadigan Vercel manzili),
   ixtiyoriy `ANTHROPIC_API_KEY`, universitet akkaunti uchun `UNIVERSITY_EMAIL` / `UNIVERSITY_PASSWORD`.
3. **Vercel** → Add New Project → shu repo, **Root Directory = `frontend`**.
   Environment: `NEXT_PUBLIC_API_URL` = Render backend manzili (masalan `https://uniskill-api.onrender.com`).
4. Vercel manzilini Render'dagi `CORS_ORIGINS` ga yozing va backend'ni qayta ishga tushiring.
5. Haqiqiy foydalanuvchilar uchun `SEED_DEMO=0` qiling.

Eslatma: bepul Render xizmati 15 daqiqa harakatsizlikdan keyin uxlaydi (birinchi so'rov ~30–60 s),
bepul PostgreSQL esa cheklangan muddatli bo'lishi mumkin: himoya uchun yetarli, doimiy ishlash uchun pullik tarif kerak.

## Qanday ishlaydi
- Talaba kasb tanlaydi → dalil yuklaydi → AI dastlabki baho beradi → **universitet (ekspert) tasdiqlaydi**.
- Skill Gap va pasport faqat **tasdiqlangan** dalillarga tayanadi; o'zini baholash tasdiq hisoblanmaydi.
- Ish beruvchi faqat rozilik bergan talabalarni va faqat tasdiqlangan ko'nikmalarni ko'radi.
- Universitet anonim, umumlashtirilgan tahlilni ko'radi.
- Universitet (ekspert) roli ochiq ro'yxatdan o'tishda yo'q: u muhit o'zgaruvchilari orqali yaratiladi.
