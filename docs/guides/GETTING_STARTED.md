# 🚀 AutoCbot - Guía de Inicio Rápido

## 📝 Requisitos Previos

### Software Necesario:
- **Python 3.10 o superior** ([Descargar aquí](https://www.python.org/downloads/))
- **Node.js 16 o superior** ([Descargar aquí](https://nodejs.org/))
- **Git** ([Descargar aquí](https://git-scm.com/))

### Cuentas Necesarias (Opcional para testing):
- Cuenta en Binance (o cualquier exchange compatible con CCXT)
- API Keys de Binance (para trading real)

---

## 🏃 Inicio Rápido - 5 Minutos

### 1. Clonar el Repositorio

```bash
# Clonar el proyecto
git clone https://github.com/CrisRS06/AutoCbot.git
cd AutoCbot
```

### 2. Configurar Backend (API)

```bash
# Ir a la carpeta backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo de configuración
cp .env.example .env

# Editar .env con tus configuraciones
# (usa tu editor favorito: nano, vim, VSCode, etc.)
nano .env
```

### 3. Configurar Variables de Entorno

Edita el archivo `.env` con estos valores mínimos:

```bash
# Seguridad (IMPORTANTE: Genera uno único para producción)
SECRET_KEY=tu_clave_secreta_super_segura_cambiala_en_produccion

# Base de datos (SQLite para desarrollo)
DATABASE_URL=sqlite:///./autocbot.db

# JWT Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys de Exchanges (OPCIONAL - solo para trading real)
BINANCE_API_KEY=tu_api_key_de_binance
BINANCE_SECRET=tu_secret_de_binance

# Modo de operación
DEBUG=True
DRY_RUN=True  # IMPORTANTE: Mantén en True para paper trading
```

### 4. Inicializar Base de Datos

```bash
# Ejecutar migraciones
alembic upgrade head

# O si alembic no está disponible, la DB se crea automáticamente al iniciar
```

### 5. Iniciar el Backend

```bash
# Desde la carpeta backend/
python main.py

# Deberías ver:
# 🚀 Starting AutoCbot Backend...
# ✅ Database initialized successfully
# ✅ All services initialized
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Probar el Backend

Abre tu navegador en: http://localhost:8000

Deberías ver:
```json
{
  "name": "AutoCbot API",
  "version": "1.0.0",
  "status": "operational",
  "description": "AI-Powered Crypto Trading System"
}
```

### 7. Configurar Frontend (Opcional)

```bash
# En otra terminal, ir a la carpeta frontend
cd ../frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Deberías ver:
# VITE v4.x.x  ready in xxx ms
# ➜  Local:   http://localhost:3000/
```

### 8. Acceder a la Aplicación

Abre tu navegador en: http://localhost:3000

---

## 🎮 Primeros Pasos en la Aplicación

### 1. Crear tu Primera Cuenta

```
http://localhost:3000/register

Email: tu@email.com
Password: MiPassword123!  (debe cumplir requisitos)
```

### 2. Iniciar Sesión

```
http://localhost:3000/login
```

### 3. Configurar tu Primera Estrategia

1. Ve a **"Strategies"** en el menú
2. Click en **"Create New Strategy"**
3. Elige un tipo (ej: "Momentum")
4. Configura parámetros básicos:
   - Símbolos: BTC/USDT, ETH/USDT
   - Timeframe: 5m
   - Risk: Medium

### 4. Hacer tu Primer Backtest

1. Selecciona tu estrategia
2. Click en **"Backtest"**
3. Configura fechas:
   - Start Date: hace 30 días
   - End Date: hoy
4. Click en **"Run Backtest"**
5. Ve los resultados: profit, win rate, drawdown, etc.

### 5. Activar Paper Trading

1. En la estrategia, click **"Activate"**
2. Asegúrate que `DRY_RUN=True` en tu .env
3. El bot comenzará a operar con dinero virtual
4. Monitorea en el dashboard

---

## 🔧 Comandos Útiles

### Backend

```bash
# Iniciar servidor en modo desarrollo
python main.py

# Ejecutar tests
pytest

# Ver logs
tail -f logs/autocbot.log

# Limpiar base de datos
rm autocbot.db
alembic upgrade head
```

### Frontend

```bash
# Iniciar desarrollo
npm run dev

# Build para producción
npm run build

# Preview de producción
npm run preview
```

---

## 🐛 Solución de Problemas

### Error: "Module not found"
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error: "Port already in use"
```bash
# Cambiar puerto en main.py (línea ~170)
uvicorn.run("main:app", host="0.0.0.0", port=8001)
```

### Error: "Database locked"
```bash
# Detener todos los procesos y reiniciar
pkill -f python
python main.py
```

### Error: "CORS policy"
```bash
# Verificar en backend/utils/config.py que tu frontend está en CORS_ORIGINS
CORS_ORIGINS = ["http://localhost:3000"]
```

---

## 📊 Endpoints de la API

### Documentación Interactiva

Una vez que el backend esté corriendo, visita:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Aquí puedes probar todos los endpoints directamente desde el navegador.

### Endpoints Principales

```bash
# Health Check
GET http://localhost:8000/health

# Registrar usuario
POST http://localhost:8000/api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# Login
POST http://localhost:8000/api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# Obtener estrategias
GET http://localhost:8000/api/v1/strategy/list
Authorization: Bearer {tu_token}

# Crear estrategia
POST http://localhost:8000/api/v1/strategy/
Authorization: Bearer {tu_token}
{
  "name": "My First Strategy",
  "type": "momentum",
  ...
}

# Ejecutar backtest
POST http://localhost:8000/api/v1/backtest/run
Authorization: Bearer {tu_token}
{
  "strategy_name": "My First Strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-11-01",
  ...
}

# Obtener señales de trading
GET http://localhost:8000/api/v1/trading/signals
Authorization: Bearer {tu_token}
```

---

## 🎯 Modo Paper Trading vs Real Trading

### Paper Trading (Sin Riesgo) 📝

**Configuración en `.env`:**
```bash
DRY_RUN=True
ENABLE_PAPER_TRADING=True
```

**Características:**
- ✅ Dinero virtual (no real)
- ✅ Todas las funcionalidades del bot
- ✅ Prueba estrategias sin riesgo
- ✅ Datos de mercado en tiempo real
- ✅ Simulación de órdenes

**Ideal para:**
- Aprender a usar el sistema
- Probar nuevas estrategias
- Ajustar parámetros
- Ganar confianza

### Real Trading (Dinero Real) 💰

**Configuración en `.env`:**
```bash
DRY_RUN=False
ENABLE_PAPER_TRADING=False

# REQUERIDO: API Keys reales de tu exchange
BINANCE_API_KEY=tu_api_key_real
BINANCE_SECRET=tu_secret_real
```

**⚠️ ADVERTENCIAS:**
- Solo después de probar extensivamente en paper trading
- Comienza con pequeñas cantidades
- Usa stop-loss siempre
- Monitorea constantemente al inicio
- El trading de criptomonedas es de alto riesgo

---

## 🔐 Seguridad - Configuración Inicial

### 1. Cambiar SECRET_KEY

**CRÍTICO**: Genera una clave única para producción:

```bash
# En Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copiar el resultado a .env
SECRET_KEY=el_resultado_aqui
```

### 2. Proteger tus API Keys

```bash
# NUNCA compartas tus API keys
# NUNCA las subas a GitHub
# USA permisos mínimos en Binance:
#   - ✅ Read Info
#   - ✅ Enable Trading
#   - ❌ Enable Withdrawals (DESACTIVADO)
```

### 3. Base de Datos

```bash
# Para producción, cambia a PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/autocbot
```

---

## 📚 Recursos Adicionales

### Documentación
- [API Documentation](http://localhost:8000/docs) - Una vez corriendo el backend
- [PRODUCTION_READINESS_REPORT.md](./PRODUCTION_READINESS_REPORT.md) - Reporte de seguridad
- [POST_DEPLOYMENT_SETUP.md](./POST_DEPLOYMENT_SETUP.md) - Configuración post-despliegue

### Archivos de Configuración Importantes
- `backend/.env` - Variables de entorno
- `backend/utils/config.py` - Configuración de la aplicación
- `backend/main.py` - Punto de entrada del servidor

### Logs y Debugging
- Logs se muestran en la terminal
- Configurar nivel de log en `.env`: `LOG_LEVEL=DEBUG`

---

## 🎓 Próximos Pasos

1. ✅ **Instalar y correr localmente** (estás aquí)
2. ⏭️ Crear tu primera estrategia
3. ⏭️ Ejecutar backtests
4. ⏭️ Activar paper trading
5. ⏭️ Analizar resultados
6. ⏭️ Optimizar estrategia
7. ⏭️ (Opcional) Pasar a real trading

---

## 🆘 ¿Necesitas Ayuda?

### Comunidad
- GitHub Issues: [Reportar problemas](https://github.com/CrisRS06/AutoCbot/issues)
- Discord: [Unirse a la comunidad](#) (si existe)

### Errores Comunes
- Consulta la sección "Solución de Problemas" arriba
- Revisa los logs en la terminal
- Verifica que todas las dependencias estén instaladas
- Asegúrate que los puertos 8000 y 3000 estén libres

---

**¡Feliz Trading! 🚀📈**

*Recuerda: El trading de criptomonedas implica riesgos. Esta herramienta es educativa. Nunca inviertas más de lo que puedes permitirte perder.*
