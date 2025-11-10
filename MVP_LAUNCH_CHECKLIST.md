# 🚀 MVP LAUNCH CHECKLIST - AutoCbot

**Target:** Despliegue a producción en <48 horas
**Estrategia:** Preview → Smoke Tests → Production con monitoreo activo
**Rollback Time:** <5 minutos si falla

---

## PRE-LAUNCH (Completar ANTES de deployment)

### 1. Configuración de Entornos ⏳

- [ ] **Crear `.env.production`** con valores reales
  ```bash
  SECRET_KEY=<generar_con_secrets.token_urlsafe_32>
  DEBUG=false
  DATABASE_URL=sqlite:///./autocbot_prod.db
  BINANCE_API_KEY=<real_or_empty>
  BINANCE_SECRET=<real_or_empty>
  CORS_ORIGINS=https://autocbot-frontend.vercel.app

  # Feature Flags (MVP - mayoría en false)
  FEATURE_ENABLE_ML_STRATEGY=false
  FEATURE_ENABLE_BACKTEST=false
  FEATURE_ENABLE_ADVANCED_METRICS=false
  FEATURE_ENABLE_TELEGRAM=false
  ```

- [ ] **Crear `docker-compose.prod.yml`**
  - Sin `--reload`
  - Sin `npm run dev`
  - Con health checks
  - Sin volumes de desarrollo

- [ ] **Validar `.dockerignore`** (✅ Ya creado)

### 2. Código MVP ⏳

- [ ] **Implementar feature flags básicos**
  - `backend/utils/feature_flags.py`
  - `frontend/src/lib/featureFlags.ts`

- [ ] **Aplicar autenticación a endpoints críticos** (P0)
  ```python
  # En /api/trading.py, /api/portfolio.py, /api/strategy.py, /api/settings.py
  from utils.auth import get_current_user

  @router.post("/order")
  async def create_order(..., current_user: User = Depends(get_current_user)):
      # ...
  ```

- [ ] **Ocultar features no-MVP con flags**
  - Estrategias ML en frontend
  - Backtest panel
  - Métricas avanzadas

- [ ] **Simplificar Settings page**
  - Solo mostrar: API keys, Risk level (Low/Medium/High), Max trades
  - Ocultar: 20+ configuraciones avanzadas

### 3. Base de Datos ⏳

- [ ] **Corregir User.hashed_password nullable**
  ```sql
  ALTER TABLE users MODIFY COLUMN hashed_password VARCHAR(255) NOT NULL;
  ```

- [ ] **Crear migración de Alembic**
  ```bash
  cd backend
  alembic revision -m "Make user password required for MVP"
  # Edit migration to set NOT NULL
  alembic upgrade head
  ```

- [ ] **Seed database con estrategia base**
  ```python
  # Script: backend/scripts/seed_mvp.py
  # Crear Mean Reversion Base strategy pre-configurada
  ```

### 4. Tests Críticos ⏳

- [ ] **Ejecutar tests existentes**
  ```bash
  cd backend
  pytest tests/unit/test_risk_manager.py -v
  # Todos deben pasar
  ```

- [ ] **Crear smoke tests MVP**
  ```bash
  # backend/tests/smoke/test_mvp_flow.py
  # 1. Register user
  # 2. Login
  # 3. Set API keys
  # 4. Get strategies
  # 5. Health check
  ```

### 5. Deployment Config ⏳

**Opción A: Vercel + Railway/Render**
- [ ] Backend en Railway/Render
- [ ] Frontend en Vercel
- [ ] Environment variables configuradas

**Opción B: Docker Compose en VPS**
- [ ] VPS configurado (Ubuntu 22.04)
- [ ] Docker y docker-compose instalados
- [ ] Nginx reverse proxy
- [ ] SSL con Let's Encrypt

---

## DEPLOYMENT TO PREVIEW 🔍

### Step 1: Deploy Backend to Preview

**Railway/Render:**
```bash
# Push branch
git push origin claude/system-quality-audit-011CUyJSueAC1QkC1psDzbMM

# Railway auto-deploys from GitHub
# O manual: railway up (si Railway CLI instalado)
```

**Docker Compose (VPS):**
```bash
# SSH to VPS
ssh user@vps-ip

# Clone/pull repo
git clone <repo> || git pull

# Build y up
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

- [ ] **Backend URL preview:** `https://autocbot-api-preview.railway.app` (ejemplo)
- [ ] **Health check:** `GET /health` → Status 200 + "healthy"
- [ ] **Test manual:** `POST /api/v1/auth/register` → Status 201

### Step 2: Deploy Frontend to Preview

**Vercel:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy preview
cd frontend
vercel --prod=false

# O push branch y Vercel auto-deploys
git push origin <branch>
```

- [ ] **Frontend URL preview:** `https://autocbot-<hash>.vercel.app`
- [ ] **Conectar a backend preview** (env var `NEXT_PUBLIC_API_URL`)
- [ ] **Test manual:** Abrir en navegador, navegar a dashboard

### Step 3: Smoke Tests en Preview 🧪

- [ ] **Test 1: Health Check**
  ```bash
  curl https://autocbot-api-preview.railway.app/health
  # Expect: {"status": "healthy", ...}
  ```

- [ ] **Test 2: Register User**
  ```bash
  curl -X POST https://autocbot-api-preview.railway.app/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email": "test@mvp.com", "password": "TestMVP123!"}'
  # Expect: 201 + user object
  ```

- [ ] **Test 3: Login**
  ```bash
  curl -X POST https://autocbot-api-preview.railway.app/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "test@mvp.com", "password": "TestMVP123!"}'
  # Expect: 200 + access_token
  ```

- [ ] **Test 4: Get Strategies (Authenticated)**
  ```bash
  TOKEN=<from_login>
  curl https://autocbot-api-preview.railway.app/api/v1/strategy/list \
    -H "Authorization: Bearer $TOKEN"
  # Expect: 200 + [mean_reversion_base]
  ```

- [ ] **Test 5: Frontend Login Flow**
  - Abrir frontend preview
  - Click "Register"
  - Crear cuenta
  - Login
  - Navegar a Dashboard
  - **Expect:** Sin errores de consola, dashboard muestra layout

- [ ] **Test 6: Settings API Keys**
  - Login en frontend
  - Ir a Settings
  - Ingresar fake API keys
  - Click "Save"
  - **Expect:** Success toast, settings persisten al refrescar

### Step 4: Métricas Iniciales (Baseline) 📊

- [ ] **Backend Latency**
  ```bash
  # P50, P95, P99
  for i in {1..100}; do
    curl -w "%{time_total}\n" -o /dev/null -s https://autocbot-api-preview.railway.app/api/v1/market/overview
  done | sort -n
  # Anotar P50 (línea 50), P95 (línea 95)
  ```
  - P50: _____ ms
  - P95: _____ ms

- [ ] **Frontend Load Time**
  - Lighthouse en preview URL
  - **Anotar:**
    - FCP (First Contentful Paint): _____ ms
    - LCP (Largest Contentful Paint): _____ ms
    - TBT (Total Blocking Time): _____ ms

- [ ] **Memory Usage (Backend)**
  ```bash
  # Railway dashboard o docker stats
  docker stats autocbot-backend --no-stream
  ```
  - Memory: _____ MB

---

## PRODUCTION DEPLOYMENT 🚀

### Pre-Flight Checklist ✈️

- [ ] **Todos los smoke tests pasaron en preview**
- [ ] **Métricas de preview dentro de objetivos**
  - API Latency P95 <500ms ✅/❌
  - Frontend LCP <2.5s ✅/❌
  - 0 errores de consola ✅/❌
- [ ] **Plan de rollback listo y ensayado**
- [ ] **Backup de base de datos tomado**
- [ ] **Monitoreo configurado** (health checks, alertas básicas)

### Deployment Steps

- [ ] **1. Promover backend a producción**
  ```bash
  # Railway: Promote preview deployment to production
  # O en VPS:
  ssh user@prod-vps
  git pull origin main
  docker-compose -f docker-compose.prod.yml up -d --build
  ```

- [ ] **2. Promover frontend a producción**
  ```bash
  # Vercel: Deploy to production
  cd frontend
  vercel --prod

  # O merge PR a main y auto-deploy
  ```

- [ ] **3. Verificar URLs de producción**
  - Backend: `https://api.autocbot.com` (o similar)
  - Frontend: `https://autocbot.com` (o similar)

- [ ] **4. Smoke tests en producción** (repetir tests de preview)

---

## POST-DEPLOYMENT MONITORING 👀

### Primeras 2 Horas (Crítico)

- [ ] **Cada 15 minutos:** Check health endpoint
  ```bash
  watch -n 900 'curl -s https://api.autocbot.com/health | jq'
  ```

- [ ] **Revisar logs continuamente**
  ```bash
  # Railway/Render: Dashboard logs
  # VPS:
  docker-compose -f docker-compose.prod.yml logs -f --tail=100
  ```

- [ ] **Monitorear errores:**
  - Buscar "ERROR", "CRITICAL", "Exception" en logs
  - Verificar que no hay 500s en endpoints

- [ ] **Test manual del flujo completo:**
  - Registrar usuario real
  - Configurar API keys (fake o real modo paper)
  - Activar paper trading
  - Verificar dashboard actualiza

### Primeras 24 Horas

- [ ] **Check cada 2 horas:**
  - Health endpoint: ✅/❌
  - Frontend accesible: ✅/❌
  - Logs sin errores críticos: ✅/❌

- [ ] **Métricas post-deployment:**
  - Uptime: _____%
  - API Latency P95: _____ ms (vs baseline: _____)
  - Frontend LCP: _____ ms (vs baseline: _____)
  - Total usuarios registrados: _____
  - Total trades (paper): _____

### Primera Semana

- [ ] **Monitoreo diario:**
  - Revisar logs cada mañana
  - Verificar health checks
  - Validar que usuarios beta pueden operar

- [ ] **Recopilar feedback:**
  - Bugs reportados: _____
  - Feature requests: _____
  - Issues de UX: _____

---

## ROLLBACK PLAN 🔄

### Triggers de Rollback (Ejecutar inmediatamente si)

1. ❌ **Backend crashea 3+ veces en 1 hora**
2. ❌ **Error rate >5% sostenido por 10 minutos**
3. ❌ **Health check falla por >5 minutos**
4. ❌ **Usuario pierde dinero por bug** (en live trading, si habilitado)
5. ❌ **Seguridad comprometida** (API keys expuestas, etc.)

### Rollback Steps (Tiempo objetivo: <5 minutos)

**Backend Rollback:**
```bash
# Railway/Render: Revert to previous deployment (1 click en dashboard)

# VPS Docker:
ssh user@prod-vps
git log --oneline -5  # Ver commits
git reset --hard <previous_commit>
docker-compose -f docker-compose.prod.yml up -d --build

# Verificar
curl https://api.autocbot.com/health
```

**Frontend Rollback:**
```bash
# Vercel: Revert deployment (1 click en dashboard)
# O redeploy commit anterior:
git reset --hard <previous_commit>
vercel --prod
```

**Database Rollback (si es necesario):**
```bash
# Restaurar backup
cp autocbot_prod.db.backup autocbot_prod.db

# O Alembic downgrade
cd backend
alembic downgrade -1
```

### Post-Rollback

- [ ] **Verificar que versión anterior funciona**
- [ ] **Notificar a usuarios (si aplicable)**
- [ ] **Análisis de causa raíz:**
  - ¿Qué falló?
  - ¿Por qué no se detectó en preview?
  - ¿Cómo prevenir en futuro?

---

## SUCCESS CRITERIA ✅

**MVP Deployment es exitoso si después de 48 horas:**

- ✅ Uptime ≥99% (max 14 minutos de downtime)
- ✅ 0 rollbacks ejecutados
- ✅ ≥3 usuarios beta operando exitosamente
- ✅ 0 errores críticos en logs
- ✅ Health checks pasando 100% del tiempo
- ✅ API Latency P95 dentro de objetivos (<500ms)
- ✅ Frontend LCP <2.5s
- ✅ 0 reportes de pérdida de datos
- ✅ 0 reportes de security issues

**Si cumple SUCCESS CRITERIA → MVP APROBADO 🎉**

---

## NEXT STEPS POST-MVP

1. **Semana 1:** Monitoreo intensivo, bug fixes críticos
2. **Semana 2:** Recopilar feedback de usuarios beta
3. **Semana 3:** Priorizar features v1.1 según feedback
4. **Semana 4:** Planear sprint 1 (v1.1)

---

**Checklist Version:** 1.0
**Last Updated:** 2025-11-10
**Owner:** Claude Code
**Status:** READY FOR EXECUTION
