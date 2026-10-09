PU NIN SECURITY WEB ADMIN — RENDER DEPLOY KIT
============================================

អ្វីដែលបានរៀបចំ
- Render Blueprint: render.yaml
- Gunicorn production start command
- Health endpoint: /health
- Server-side sessions (Firebase tokens មិនត្រូវបានដាក់ក្នុង browser cookie)
- CSRF protection សម្រាប់ POST forms
- HTTPS secure cookie នៅពេលដំណើរការលើ Render
- មិនដាក់ .env ចូល ZIP ដើម្បីកុំឱ្យលេចធ្លាយការកំណត់ក្នុង PC

របៀប Deploy តាម Render + GitHub
1. Extract ZIP នេះលើ PC។
2. ចូល GitHub ហើយបង្កើត Repository ថ្មី Private ឧ. pu-nin-security-web-admin។
3. Upload ឯកសារ និង folder ទាំងអស់ក្នុង ZIP ទៅ root នៃ repository។ ត្រូវឱ្យ app.py, requirements.txt និង render.yaml នៅ root ដូចគ្នា។ កុំ upload .env ឬ Telegram token។
4. ចូល https://dashboard.render.com/ ហើយចុច New + > Blueprint (បើមាន)។ Connect GitHub repository ថ្មីនេះ រួច Apply។
   ប្រសិនបើប្រើ Web Service ដោយដៃ៖
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:app --workers 1 --threads 4 --timeout 120
   - Health Check Path: /health
5. នៅ Render Dashboard > Service > Environment បញ្ចូល/ពិនិត្យ៖
   - FLASK_SECRET_KEY: Generate/ប្រើ random secret វែង (Blueprint នឹង generate ឱ្យស្វ័យប្រវត្តិ)
   - FIREBASE_API_KEY: Firebase Web App apiKey ពិតរបស់ Project
   - FIREBASE_URL: https://punin-mobile-unlock-default-rtdb.asia-southeast1.firebasedatabase.app
   - TELEGRAM_BOT_TOKEN: Bot Token ពី @BotFather (អាចទុកទទេ បើមិនទាន់ភ្ជាប់)
   - TELEGRAM_CHAT_ID: Chat ID (អាចទុកទទេ បើមិនទាន់ភ្ជាប់)
6. ចុច Save Changes / Deploy។ រង់ចាំ Build និង Deploy បញ្ចប់ដោយ Live។
7. ចុច URL ដែល Render ផ្ដល់ឱ្យ ដូចជា https://your-service.onrender.com/ ។
8. សាក Health check នៅ https://your-service.onrender.com/health ត្រូវឃើញ JSON status=ok។
9. Login ដោយ Firebase Authentication Admin account ដែល UID មាន /admins/{UID} = true។
10. សាក Telegram Alert: បញ្ចូល Bot Token + Chat ID ក្នុង Render Environment រួច Save/Deploy ម្ដងទៀត។ ផ្ញើ /start ទៅ Bot ជាមុន។

ចំណុចសំខាន់អំពីសុវត្ថិភាព — សូមអានមុនបើក Public
- កុំដាក់ .env ឬ Telegram Bot Token ក្នុង GitHub; ប្រើ Render Environment Variables ប៉ុណ្ណោះ។
- Firebase Rules ចាស់ដែលអនុញ្ញាត public read លើ /approved_users អាចបង្ហាញទិន្នន័យសមាជិក និង password ដែល client ចាស់រក្សាទុកនៅទីនោះ។ កុំចាត់ទុក deployment នេះថា production-safe រហូតដល់បានកែ data model/rules និងផ្លាស់ការផ្ទៀងផ្ទាត់ member ទៅ Firebase Authentication ឬ backend ដែលមានសុវត្ថិភាព។ ការបិទ public read ដោយផ្ទាល់អាចបំបែក client ចាស់; សូមរៀបចំ migration ដាច់ដោយឡែក មុនប្ដូរ rules។
- Admin Web Starter នេះមិនទាន់មានមុខងារទាំងអស់ពី Desktop Admin ដូចជា bulk threat import, malware editor និង HWID reset។
- min_supported_version មិនបង្ខំ client ឱ្យ update ទេ លុះត្រាតែកូដ client ពិនិត្យវា។
- Render Free Web Service អាច sleep ពេលគ្មានការប្រើ ហើយការចូលលើកដំបូងក្រោយ idle អាចយឺត។
- មិនទាន់ Deploy ទៅ Render ជំនួសអ្នកទេ ព្រោះត្រូវការសិទ្ធិ GitHub/Render របស់អ្នក។ កុំផ្ញើ password ឬ token មក ChatGPT។

Official Render Flask guide: https://render.com/docs/deploy-flask
