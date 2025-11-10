# ☁️ AutoCbot - Guía de Deployment en la Nube

## 🎯 Comparación de Opciones

| Plataforma | ¿Funciona 24/7? | Backend | Frontend | Base de Datos | Costo Inicial | Mejor Para |
|------------|-----------------|---------|----------|---------------|---------------|------------|
| **PC Local** | ❌ Solo cuando esté encendida | ✅ | ✅ | ✅ | Gratis | Desarrollo/Testing |
| **Render** | ✅ | ✅ | ✅ | ✅ | $0-7/mes | **RECOMENDADO** para MVP |
| **Railway** | ✅ | ✅ | ✅ | ✅ | $5/mes | Desarrollo rápido |
| **Vercel** | ✅ | ⚠️ Limitado | ✅ | ❌ | Gratis | Solo frontend |
| **Heroku** | ✅ | ✅ | ✅ | ✅ | $7/mes | Completo |
| **VPS (DigitalOcean)** | ✅ | ✅ | ✅ | ✅ | $6/mes | Control total |

---

## 🏆 OPCIÓN RECOMENDADA: Render (Mejor Balance)

### ¿Por Qué Render?

✅ **Pros:**
- Plan gratuito disponible (con limitaciones)
- Backend y Frontend juntos
- Base de datos PostgreSQL incluida
- Funciona 24/7
- Fácil setup desde GitHub
- SSL certificado automático
- Auto-deploy desde Git

❌ **Contras:**
- Plan gratuito: backend "duerme" después de 15 min inactivo
- Plan gratuito: 750 horas/mes (suficiente para testing)
- Para 24/7 real: $7/mes por servicio

### 🚀 Deployment en Render (Paso a Paso)

#### 1. Preparar el Proyecto

**Crear `render.yaml` en la raíz del proyecto:**

```yaml
# render.yaml
services:
  # Backend API
  - type: web
    name: autocbot-api
    env: python
    region: oregon
    plan: free  # o "starter" para $7/mes sin sleep
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: autocbot-db
          property: connectionString
      - key: PYTHON_VERSION
        value: "3.11.0"
      - key: DEBUG
        value: "False"
      - key: DRY_RUN
        value: "True"
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: "30"
      - key: REFRESH_TOKEN_EXPIRE_DAYS
        value: "7"

  # Frontend (React/Vue/etc)
  - type: web
    name: autocbot-frontend
    env: static
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: frontend/dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html

# Base de datos PostgreSQL
databases:
  - name: autocbot-db
    plan: free  # 90 días gratis, luego $7/mes
    databaseName: autocbot
    user: autocbot
```

#### 2. Crear Archivos de Configuración

**Crear `backend/requirements.txt` (si no existe):**
Ya existe, pero verificar que tenga todo.

**Crear `backend/Procfile` (alternativa):**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 3. Subir a GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

#### 4. Crear Cuenta en Render

1. Ve a https://render.com
2. Registrarse con GitHub
3. Conecta tu repositorio AutoCbot

#### 5. Crear el Deployment

**Opción A: Usando render.yaml (Automático)**
```
1. En Render Dashboard, click "New +"
2. Seleccionar "Blueprint"
3. Conectar tu repositorio GitHub
4. Render detectará render.yaml automáticamente
5. Click "Apply"
```

**Opción B: Manual**

**Crear el Backend:**
```
1. New + → Web Service
2. Conectar repositorio GitHub
3. Name: autocbot-api
4. Root Directory: backend
5. Environment: Python 3
6. Build Command: pip install -r requirements.txt
7. Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
8. Plan: Free (o Starter para 24/7)
9. Advanced:
   - Add Environment Variables (ver arriba)
```

**Crear la Base de Datos:**
```
1. New + → PostgreSQL
2. Name: autocbot-db
3. Database: autocbot
4. Plan: Free (90 días)
5. Click "Create Database"
6. Copiar "Internal Database URL"
7. Pegar en backend como DATABASE_URL
```

**Crear el Frontend:**
```
1. New + → Static Site
2. Conectar repositorio
3. Root Directory: frontend
4. Build Command: npm install && npm run build
5. Publish Directory: dist
```

#### 6. Variables de Entorno en Render

En el dashboard del backend, añadir:

```bash
SECRET_KEY=<generar_uno_seguro>
DATABASE_URL=<copiar_de_la_db_creada>
DEBUG=False
DRY_RUN=True
CORS_ORIGINS=https://tu-frontend.onrender.com
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Opcional para trading real
BINANCE_API_KEY=<tu_api_key>
BINANCE_SECRET=<tu_secret>
```

#### 7. Migrar Base de Datos

Una vez desplegado, ejecutar migraciones:

**Opción A: Shell en Render**
```bash
1. En tu servicio backend, ir a "Shell"
2. Ejecutar:
   alembic upgrade head
```

**Opción B: Agregar al build command**
```yaml
buildCommand: "pip install -r requirements.txt && alembic upgrade head"
```

#### 8. Verificar Deployment

```bash
# Backend
curl https://tu-app.onrender.com/health

# Frontend
https://tu-frontend.onrender.com
```

---

## 🚂 OPCIÓN 2: Railway (Más Rápido)

### Ventajas de Railway:
- Deploy en segundos
- CLI poderoso
- $5/mes crédito gratis
- PostgreSQL incluido
- Muy fácil de usar

### 🚀 Deployment en Railway

#### 1. Crear `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. Crear Cuenta y Deploy

```bash
# Instalar CLI de Railway
npm install -g @railway/cli

# Login
railway login

# Ir a tu proyecto
cd AutoCbot/backend

# Inicializar
railway init

# Añadir PostgreSQL
railway add --plugin postgresql

# Deploy
railway up

# Ver logs
railway logs
```

#### 3. Configurar Variables

```bash
railway variables set SECRET_KEY=tu_secret_key
railway variables set DEBUG=False
railway variables set DRY_RUN=True
```

---

## ⚡ OPCIÓN 3: Vercel (Solo para Frontend + Serverless API)

### ⚠️ Limitaciones Importantes:

**NO ES IDEAL PARA AUTOCBOT porque:**
- ❌ Funciones serverless (no conexiones persistentes)
- ❌ No puede mantener bots corriendo 24/7
- ❌ No incluye base de datos
- ❌ Límite de 250MB por función
- ❌ No apto para trading en tiempo real

**Solo usar Vercel para:**
- ✅ Desplegar el frontend (React/Vue)
- ✅ API REST simple sin estado
- ✅ Landing page

### Deploy Frontend en Vercel

```bash
# Instalar CLI
npm install -g vercel

# Ir a frontend
cd frontend

# Deploy
vercel

# Seguir prompts
```

---

## 🖥️ OPCIÓN 4: VPS (DigitalOcean, Linode, Vultr)

### Mejor Para:
- ✅ Control total
- ✅ Mejor rendimiento
- ✅ Múltiples proyectos
- ✅ Configuración personalizada

### Costo:
- $6-12/mes (droplet básico)

### Setup Rápido en DigitalOcean

#### 1. Crear Droplet

```
1. Ir a digitalocean.com
2. Create → Droplets
3. Elegir Ubuntu 22.04 LTS
4. Plan: $6/mes (1GB RAM)
5. Región: cercana a ti
6. SSH key o password
7. Create Droplet
```

#### 2. Conectar por SSH

```bash
ssh root@tu_ip_del_droplet
```

#### 3. Instalar Dependencias

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar Python 3.11
apt install python3.11 python3.11-venv python3-pip -y

# Instalar PostgreSQL
apt install postgresql postgresql-contrib -y

# Instalar Nginx (reverse proxy)
apt install nginx -y

# Instalar Node.js (para frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Instalar Git
apt install git -y
```

#### 4. Clonar y Configurar Proyecto

```bash
# Clonar
cd /var/www
git clone https://github.com/CrisRS06/AutoCbot.git
cd AutoCbot

# Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crear .env
nano .env
# (copiar configuración)

# Migrar DB
alembic upgrade head
```

#### 5. Configurar Systemd (Para que corra 24/7)

```bash
# Crear servicio
nano /etc/systemd/system/autocbot.service
```

```ini
[Unit]
Description=AutoCbot Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/AutoCbot/backend
Environment="PATH=/var/www/AutoCbot/backend/venv/bin"
ExecStart=/var/www/AutoCbot/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activar servicio
systemctl daemon-reload
systemctl enable autocbot
systemctl start autocbot
systemctl status autocbot
```

#### 6. Configurar Nginx (Proxy Inverso)

```bash
nano /etc/nginx/sites-available/autocbot
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Activar sitio
ln -s /etc/nginx/sites-available/autocbot /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 7. SSL con Let's Encrypt (HTTPS)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d tu-dominio.com
```

---

## 📊 Comparación de Costos (Mensual)

| Servicio | Plan Gratuito | Plan Básico (24/7) | Plan Pro |
|----------|---------------|---------------------|----------|
| **Render** | 750hrs/mes | $7/servicio | $25 |
| **Railway** | $5 crédito | ~$10 | ~$20 |
| **Heroku** | ❌ | $7/dyno | $25 |
| **VPS** | ❌ | $6-12 | $24+ |
| **PC 24/7** | Luz eléctrica | ~$15-30 | N/A |

---

## 🎯 Recomendaciones Según tu Caso

### 1. **Solo Quiero Probar (Gratis)**
```
✅ PC Local (GETTING_STARTED.md)
- No cuesta nada
- Funciona mientras tu PC esté encendida
- Ideal para aprender
```

### 2. **Quiero Testear 24/7 (Casi Gratis)**
```
✅ Render Plan Gratuito
- Backend "duerme" tras 15min sin uso
- Se "despierta" al recibir request (tarda ~30s)
- Suficiente para paper trading casual
- 750 horas/mes gratis
```

### 3. **Quiero Trading 24/7 Real (Barato)**
```
✅ Railway ($5/mes) o Render ($7/mes)
- Siempre activo
- Auto-scale
- Backups incluidos
- Fácil de mantener
```

### 4. **Quiero Control Total (Avanzado)**
```
✅ VPS DigitalOcean ($6/mes)
- Acceso root
- Instala lo que quieras
- Mejor rendimiento
- Requiere conocimientos Linux
```

### 5. **Proyecto Serio/Producción**
```
✅ Render Pro ($25) o VPS ($24)
- Alta disponibilidad
- Monitoreo
- Backups automáticos
- Soporte
```

---

## ⚠️ Consideraciones Importantes

### 1. PC Local 24/7: ¿Vale la Pena?

**Costos Ocultos:**
```
PC consumo: 100-300W
Luz: ~$0.15/kWh (promedio)
Mes: 720 horas

100W × 720h × $0.15 = ~$10.8/mes
300W × 720h × $0.15 = ~$32.4/mes

¿Vale la pena? NO
- Gasto eléctrico similar a hosting
- PC puede fallar
- Internet puede caerse
- Sin backups automáticos
```

### 2. Trading 24/7: ¿Es Necesario?

**Depende de tu estrategia:**

```
✅ Necesitas 24/7 si:
- Haces scalping (operaciones de minutos)
- Trading en múltiples timeframes
- Quieres capturar todos los movimientos
- Bot responde a señales en tiempo real

⚠️ NO necesitas 24/7 si:
- Backtesting solamente
- Análisis diario
- Paper trading casual
- Aprendiendo el sistema
```

### 3. Base de Datos

```
SQLite (Desarrollo):
✅ Gratis
✅ Fácil
❌ No escalable
❌ No para producción multi-usuario

PostgreSQL (Producción):
✅ Robusto
✅ Escalable
✅ Backups automáticos
💰 $7-15/mes en cloud
```

---

## 🚀 Mi Recomendación Personal

### Fase 1: Aprendizaje (1-2 meses)
```bash
🏠 PC Local
- Costo: $0
- Tiempo: Cuando estudies/trabajes
- Objetivo: Aprender el sistema
```

### Fase 2: Testing 24/7 (1-3 meses)
```bash
☁️ Render Plan Gratuito o Railway ($5)
- Costo: $0-5/mes
- Tiempo: 24/7 con sleep en gratuito
- Objetivo: Probar estrategias en papel
```

### Fase 3: Trading Real
```bash
☁️ Render Starter ($7) o VPS ($12)
- Costo: $7-12/mes
- Tiempo: 24/7 real
- Objetivo: Trading automatizado
```

---

## 📝 Checklist de Deployment

### Pre-Deployment
- [ ] Código en GitHub/GitLab
- [ ] `.env.example` con variables necesarias
- [ ] `requirements.txt` actualizado
- [ ] Migraciones de DB listas
- [ ] Frontend build funciona
- [ ] Tests pasan localmente

### Deployment
- [ ] Plataforma elegida (Render/Railway/VPS)
- [ ] Base de datos PostgreSQL creada
- [ ] Variables de entorno configuradas
- [ ] SSL/HTTPS configurado
- [ ] Migraciones ejecutadas
- [ ] Health check funciona

### Post-Deployment
- [ ] Monitoreo configurado (Sentry)
- [ ] Backups automáticos
- [ ] Logs accesibles
- [ ] Alertas configuradas
- [ ] Documentación actualizada

---

## 🆘 Troubleshooting Común

### "Application Error" en Render
```bash
# Revisar logs en dashboard
# Verificar startCommand
# Confirmar requirements.txt
```

### Database Connection Error
```bash
# Verificar DATABASE_URL
# Confirmar que DB está activa
# Revisar whitelist de IPs
```

### Frontend No Conecta con Backend
```bash
# Verificar CORS_ORIGINS en backend
# Confirmar URL del backend en frontend
# Revisar variables de entorno
```

---

**¿Necesitas ayuda específica con alguna plataforma? ¡Pregúntame!** 🚀
