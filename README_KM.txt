PU NIN SECURITY WEB ADMIN + TELEGRAM ALERTS
============================================

មុខងារដែលមានក្នុង Starter នេះ
- Login តាម Firebase Authentication ហើយពិនិត្យ /admins/{UID} = true
- Dashboard សង្ខេបចំនួន Pending / Members / Malware / Threats / Notifications
- Pending Users: Approve ឬ Delete
- Approved Members: មើលបញ្ជី និង Delete
- Publish app_version update manifest
- បង្កើត Customer Notification
- Telegram alert សម្រាប់ login, approve/delete, update និង notification

វិធីដំណើរការលើ Windows PC (Local)
1. Extract ZIP ទៅ folder ធម្មតា ឧ. C:\PU_NIN_WEB_ADMIN (កុំដំណើរការនៅក្នុង ZIP)។
2. Double-click START_LOCAL.bat។ បើគ្មាន Python 3.11/3.12 x64 វានឹងទាញយក Python 3.12.10 x64 ពី python.org ហើយដំឡើងស្វ័យប្រវត្តិ (សម្រាប់ Windows user បច្ចុប្បន្ន)។ ត្រូវមាន Internet។
3. វាបង្កើត .venv និងដំឡើង packages ស្វ័យប្រវត្តិ។
4. វាបង្កើតឯកសារ .env ហើយបើក Notepad។ បំពេញតម្លៃខាងក្រោម រួច Save។
5. Double-click START_LOCAL.bat ម្ដងទៀត។ បើក http://127.0.0.1:5000។
6. Login ដោយ Firebase Authentication email/password របស់ Admin។

របៀបរក Firebase API Key
- Firebase Console > Project settings > General > Your apps > Web app > SDK setup/configuration។
- ចម្លងតែ apiKey ទៅ FIREBASE_API_KEY ក្នុង .env។ FIREBASE_URL បានដាក់ជាមុនហើយ។
- Firebase Console > Realtime Database > Data: ត្រូវមាន /admins/{FIREBASE_AUTH_UID} = true សម្រាប់ UID របស់ Admin។
- UID មើលបានក្នុង Firebase Console > Authentication > Users។ កុំដាក់ email ជំនួស UID។

របៀបបើក Telegram Alert
1. ក្នុង Telegram ស្វែងរក @BotFather, ប្រើ /newbot ហើយរក្សាទុក Bot Token ជាសម្ងាត់។
2. ផ្ញើសារ /start ទៅ bot ថ្មីរបស់អ្នក។
3. ដើម្បីរក Chat ID៖ បើក https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates ក្នុង browser បន្ទាប់ពីផ្ញើ /start។
   រកលេខក្នុង message.chat.id។ កុំចែករំលែក URL នេះ ព្រោះវាមាន Bot Token។
4. ដាក់ Token ក្នុង TELEGRAM_BOT_TOKEN និងលេខ Chat ID ក្នុង TELEGRAM_CHAT_ID នៃ .env។
5. Save .env ហើយបិទ/បើក START_LOCAL.bat ឡើងវិញ។

សំខាន់៖
- កុំផ្ញើឯកសារ .env ទៅអ្នកដទៃ និងកុំដាក់ Token/Password ក្នុងកូដ ឬ ZIP ដែលចែកចាយ។
- Local URL 127.0.0.1 អាចប្រើបានតែលើ PC នោះ។ វាមិនទាន់ជា public website ដែលអាចចូលពីគ្រប់ទីកន្លែងទេ។
- មុនដាក់អនឡាញ ត្រូវមាន HTTPS, production WSGI server, CSRF protection, session/security hardening និងសាកល្បង Firebase Rules។ កុំបើក Flask development server ទៅ Internet។
- កំណែ desktop/client បច្ចុប្បន្នមានការរក្សាទុក password ក្នុង approved_users; នេះជាហានិភ័យ។ គួរផ្លាស់ទៅ Firebase Authentication មុនប្រើប្រាស់ជាសាធារណៈ។
- ការកំណត់ min_supported_version មិនបង្ខំ client ចាស់ឱ្យ update ទេ លុះត្រាតែកូដ client ពិនិត្យ field នេះ។
- នេះជាកំណែ Starter មិនទាន់មានគ្រប់ផ្ទាំងរបស់ desktop Admin ដូចជា bulk threat import, malware record editing និង member edit/HWID reset។


ភ្ជាប់ Telegram ដោយស្វ័យប្រវត្តិ (មិនចាំបាច់កែ .env ដោយដៃ)
1. បើក Telegram រក @BotFather ហើយបង្កើត Bot ប្រសិនបើមិនទាន់មាន។
2. បើក Chat ជាមួយ Bot របស់អ្នក ហើយផ្ញើ /start។
3. រក្សាទុក Chat ID របស់អ្នក។
4. ចូល Folder កម្មវិធី ហើយចុច SETUP_TELEGRAM.bat។
5. បញ្ចូល Bot Token និង Chat ID នៅក្នុងផ្ទាំងខ្មៅ។ កុំផ្ញើ Token មក ChatGPT ឬអ្នកដទៃ។
6. វានឹងសាកល្បង Telegram API ផ្ញើសារសាកល្បង ហើយរក្សាទុកក្នុង .env បើជោគជ័យ។
7. បិទ Web Admin ហើយបើក START_LOCAL.bat ឡើងវិញ ដើម្បីឱ្យ Alert ដំណើរការ។

Telegram Alert ត្រូវបានបញ្ជូននៅពេល Admin Login, Approve/Delete Member, Publish Client Update និង Customer Notice។
