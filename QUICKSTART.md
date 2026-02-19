# 🚀 Quick Start Guide

## सबसे तेजी से शुरू करें - Fastest way to get started!

---

## Windows पर 3 Steps:

### Step 1: setup.bat चलाएं
```
Double-click setup.bat
```

### Step 2: Admin Details दें
```
Enter admin username and password
```

### Step 3: Server चलाएं
```
python manage.py runserver
```

---

## Linux/Mac पर 3 Steps:

### Step 1: Permission दें
```bash
chmod +x setup.sh
```

### Step 2: setup.sh चलाएं
```bash
./setup.sh
```

### Step 3: Server चलाएं
```bash
source venv/bin/activate
python manage.py runserver
```

---

## Termux (Android) पर:

```bash
pip install django django-ninja pillow python-dateutil
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

---

## 🌐 Access Points:

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/ | Dashboard (बिना login के access करें) |
| http://127.0.0.1:8000/api/ | API Endpoints |
| http://127.0.0.1:8000/admin/ | Admin Panel (login करें) |

---

## 📱 Test API Immediately:

### Browser में:
```
http://127.0.0.1:8000/api/goats/
```

### cURL से:
```bash
curl http://127.0.0.1:8000/api/stats/dashboard/
```

### Python से:
```python
import requests
response = requests.get('http://127.0.0.1:8000/api/goats/')
print(response.json())
```

---

## 🆘 Troubleshooting:

### Port 8000 already in use?
```bash
python manage.py runserver 8001
```

### Permission denied on setup.sh?
```bash
chmod +x setup.sh
./setup.sh
```

### Django not found?
```bash
pip install django django-ninja
```

### Database issues?
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 🎯 Next Steps:

1. **Dashboard देखें** - Stats और recent records
2. **API Docs पढ़ें** - सभी endpoints समझें
3. **Admin Panel खोलें** - Data manually add करें
4. **API Test करें** - curl या Postman से
5. **Mobile App बनाएं** - React Native / Flutter के साथ

---

## 💾 Important Commands:

```bash
# Create superuser
python manage.py createsuperuser

# Dump database
python manage.py dumpdata > backup.json

# Load database
python manage.py loaddata backup.json

# Shell में test करें
python manage.py shell

# Migrate करें
python manage.py migrate

# Makemigrations करें
python manage.py makemigrations
```

---

**Ready? शुरू करो! 🚀**
