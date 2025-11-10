# MVP SCOPE & TRADE-OFFS - AutoCbot
**Fecha:** 10 de noviembre de 2025
**Estrategia:** Fast-track to Production
**Objetivo:** Lanzar MVP funcional en <48 horas con funcionalidad core operativa

---

## 🎯 FLUJO CRÍTICO DE VALOR (MVP Core)

**Usuario Objetivo:** Trader individual que quiere automatizar trading de crypto con estrategias predefinidas

**Flujo Core (Camino Feliz):**
```
1. Usuario se registra → Login
2. Configura API keys de Binance (solo lectura + trading, SIN retiros)
3. Selecciona estrategia pre-configurada (Mean Reversion Base)
4. Activa paper trading (dry-run mode)
5. Monitorea dashboard en tiempo real
6. Ve trades ejecutados y performance
7. (Después de validación) Activa live trading con capital limitado
```

**Métricas de Éxito MVP:**
- Usuario puede hacer paper trading en <10 minutos desde registro
- Dashboard muestra métricas en tiempo real
- No hay errores críticos en flujo core
- Sistema puede correr 24/7 sin intervención

---

## 📊 CLASIFICACIÓN MoSCoW

### MUST HAVE ✅ (Crítico para MVP - Mantener)

#### Autenticación Básica
- ✅ **JWT authentication** (YA IMPLEMENTADO)
- ✅ Login/Register endpoints (YA IMPLEMENTADO)
- ⚠️ **SIMPLIFICAR:** Solo email/password (sin OAuth, sin 2FA por ahora)
- ⚠️ **SIMPLIFICAR:** Sin verificación de email (agregar después)

#### Trading Core
- ✅ Conexión a Binance (paper trading)
- ✅ Estrategia Mean Reversion Base (pre-configurada)
- ✅ Crear/cancelar órdenes
- ✅ Ver posiciones abiertas
- ✅ Dashboard con métricas básicas

#### Configuración Esencial
- ✅ Settings: API keys Binance
- ✅ Settings: Preferencias de riesgo básicas
- ⚠️ **SIMPLIFICAR:** Solo USDT como stake currency
- ⚠️ **SIMPLIFICAR:** Solo BTC/USDT y ETH/USDT (2 pares)

#### Seguridad Mínima
- ✅ Rate limiting básico (120 req/min)
- ✅ CORS configurado
- ✅ Security headers
- ⚠️ **TRADE-OFF:** API keys sin encriptar en BD por ahora (agregar después)

#### Monitoreo Básico
- ✅ Dashboard con profit/loss
- ✅ Lista de trades recientes
- ✅ Health check endpoint

### SHOULD HAVE 🟡 (Importante - Simplificar o Feature Flag)

#### Estrategias Adicionales
- 🚩 **FEATURE FLAG:** `enable_ml_strategy`
  - Default: `false` (ocultar)
  - ML-enhanced strategy requiere modelo entrenado
  - Habilitar solo después de validar estrategia base

#### Backtesting
- 🚩 **FEATURE FLAG:** `enable_backtest`
  - Default: `false` (ocultar UI)
  - Funcionalidad existe pero puede ser pesada
  - Habilitar gradualmente

#### Portfolio Analytics
- ⚠️ **SIMPLIFICAR:** Solo métricas básicas
  - Total P&L, Win Rate, Total Trades
  - Ocultar: Sharpe ratio, Sortino, Calmar (cálculos complejos)

#### Multi-Usuario
- ⚠️ **SIMPLIFICAR:** MVP es single-tenant
  - Auth existe pero sin separación estricta de datos
  - Cada deployment = 1 usuario
  - Multi-tenant viene después

### COULD HAVE 🔵 (Deseable - Aplazar)

#### Features Aplazadas para Post-MVP
- ❌ **APLAZAR:** ML-enhanced strategy
- ❌ **APLAZAR:** Múltiples exchanges (solo Binance)
- ❌ **APLAZAR:** Telegram notifications
- ❌ **APLAZAR:** Email notifications
- ❌ **APLAZAR:** SMS alerts
- ❌ **APLAZAR:** Custom strategy builder (UI visual)
- ❌ **APLAZAR:** Social sentiment analysis avanzado
- ❌ **APLAZAR:** Tax calculator (Costa Rica compliance)

#### Integraciones Externas (No Core)
- ❌ **APLAZAR:** CoinGecko API (solo si gratis)
- ❌ **APLAZAR:** LunarCrush API
- ❌ **APLAZAR:** Glassnode API
- ❌ **APLAZAR:** Messari API

#### Optimizaciones
- ❌ **APLAZAR:** Redis caching
- ❌ **APLAZAR:** PostgreSQL (usar SQLite en MVP)
- ❌ **APLAZAR:** WebSocket optimizations
- ❌ **APLAZAR:** CDN para assets

### WON'T HAVE (Later) ⏸️ (Roadmap Futuro)

- VPS deployment automation
- Automated hyperparameter optimization
- Multi-strategy portfolio allocation
- Risk management dashboard avanzado
- Audit logs detallados
- User management (admin panel)
- Payment integration (subscriptions)
- White-label capabilities

---

## 🚩 FEATURE FLAGS REGISTRY

### Implementación
**Archivo:** `backend/utils/feature_flags.py`

```python
from pydantic_settings import BaseSettings

class FeatureFlags(BaseSettings):
    # ML Features
    enable_ml_strategy: bool = False
    enable_sentiment_analysis: bool = False

    # Advanced Features
    enable_backtest: bool = False
    enable_custom_strategies: bool = False
    enable_multi_exchange: bool = False

    # Notifications
    enable_telegram: bool = False
    enable_email: bool = False

    # Analytics
    enable_advanced_metrics: bool = False
    enable_tax_calculator: bool = False

    class Config:
        env_prefix = "FEATURE_"

flags = FeatureFlags()
```

**Archivo:** `frontend/src/lib/featureFlags.ts`

```typescript
export const featureFlags = {
  enableMLStrategy: process.env.NEXT_PUBLIC_ENABLE_ML_STRATEGY === 'true',
  enableBacktest: process.env.NEXT_PUBLIC_ENABLE_BACKTEST === 'true',
  enableAdvancedMetrics: process.env.NEXT_PUBLIC_ENABLE_ADVANCED_METRICS === 'true',
  enableTelegramNotifications: process.env.NEXT_PUBLIC_ENABLE_TELEGRAM === 'true',
}
```

### Uso en Código

**Backend:**
```python
from utils.feature_flags import flags

@router.get("/strategies")
async def list_strategies():
    strategies = [base_strategy]

    if flags.enable_ml_strategy:
        strategies.append(ml_strategy)

    return strategies
```

**Frontend:**
```typescript
{featureFlags.enableBacktest && (
  <BacktestPanel />
)}
```

### Flags por Entorno

**Development (.env.development):**
```bash
FEATURE_ENABLE_ML_STRATEGY=true
FEATURE_ENABLE_BACKTEST=true
FEATURE_ENABLE_ADVANCED_METRICS=true
```

**Production (.env.production):**
```bash
FEATURE_ENABLE_ML_STRATEGY=false
FEATURE_ENABLE_BACKTEST=false
FEATURE_ENABLE_ADVANCED_METRICS=false
```

---

## ⚡ SIMPLIFICACIONES PARA MVP

### 1. Autenticación Simplificada
**Antes (Complejo):**
- OAuth providers (Google, GitHub)
- Email verification
- 2FA
- Password reset con email
- Session management con Redis

**MVP (Simple):**
- Solo email + password
- JWT con expiracion estándar
- Password reset manual (contactar soporte)
- Sin verificación de email
- Session en memoria (stateless JWT)

**Trade-off:** Seguridad reducida, pero suficiente para MVP con usuarios beta controlados.

### 2. Base de Datos Simplificada
**Antes (Complejo):**
- PostgreSQL en producción
- Connection pooling
- Read replicas
- Backups automáticos off-site

**MVP (Simple):**
- SQLite file-based
- Single instance
- Backup manual diario
- Migrar a Postgres solo si crece

**Trade-off:** No escalable, pero perfecto para <100 usuarios MVP.

### 3. Estrategias Simplificadas
**Antes (Complejo):**
- 10+ estrategias configurables
- Custom strategy builder
- ML-enhanced con modelos entrenados
- Backtesting en paralelo

**MVP (Simple):**
- 1 estrategia: Mean Reversion Base
- Parámetros fijos (pre-configurados)
- Sin ML (feature flag)
- Sin backtest UI (feature flag)

**Trade-off:** Menos flexibilidad, pero más confiable y fácil de validar.

### 4. Pares de Trading Simplificados
**Antes (Complejo):**
- 50+ pares crypto
- Configuración dinámica
- Auto-discovery de pares

**MVP (Simple):**
- Solo 2 pares: BTC/USDT, ETH/USDT
- Hardcoded en configuración
- Validación estricta

**Trade-off:** Menos oportunidades, pero más fácil de monitorear y debuggear.

### 5. Observabilidad Simplificada
**Antes (Complejo):**
- Prometheus + Grafana
- Distributed tracing (Jaeger)
- Log aggregation (ELK stack)
- Sentry para errors
- PagerDuty para alertas

**MVP (Simple):**
- Logs a stdout (capturados por Vercel/Railway)
- Health check endpoint
- Error tracking básico (console.error)
- Alertas manuales (revisar dashboard)

**Trade-off:** Menos visibilidad, pero suficiente para MVP pequeño.

### 6. Frontend Simplificado
**Antes (Complejo):**
- 6 páginas completas
- Analytics avanzados (gráficos complejos)
- Settings con 20+ opciones
- Customización de UI

**MVP (Simple):**
- 3 páginas core: Dashboard, Trading, Settings
- Métricas básicas (cards simples)
- Settings: solo API keys y 3-4 opciones core
- UI fixed (sin dark mode toggle, sin customización)

**Trade-off:** Menos features, pero más enfocado y rápido de mantener.

---

## 🎚️ EXPERIENCIAS DEGRADADAS CLARAS

### Cuando Feature está Deshabilitado

**Backtest Deshabilitado:**
```typescript
{!featureFlags.enableBacktest && (
  <div className="bg-muted p-4 rounded-lg">
    <p className="text-sm text-muted-foreground">
      📊 Backtesting feature coming soon!
      Focus on paper trading for now.
    </p>
  </div>
)}
```

**ML Strategy Deshabilitado:**
```typescript
{!featureFlags.enableMLStrategy && (
  <Alert>
    <AlertTitle>ML Strategy Not Available</AlertTitle>
    <AlertDescription>
      Advanced ML-powered strategies are coming in the next release.
      The base mean reversion strategy is proven and reliable.
    </AlertDescription>
  </Alert>
)}
```

**Advanced Metrics Deshabilitado:**
```typescript
// Mostrar solo métricas básicas
<div className="grid grid-cols-3 gap-4">
  <MetricCard title="Total P&L" value={pnl} />
  <MetricCard title="Win Rate" value={winRate} />
  <MetricCard title="Total Trades" value={totalTrades} />

  {/* Ocultar métricas avanzadas */}
  {featureFlags.enableAdvancedMetrics && (
    <>
      <MetricCard title="Sharpe Ratio" value={sharpe} />
      <MetricCard title="Sortino Ratio" value={sortino} />
      <MetricCard title="Max Drawdown" value={maxDD} />
    </>
  )}
</div>
```

---

## 📉 REDUCCIÓN DE COMPLEJIDAD (Antes vs MVP)

| Componente | Antes | MVP | Reducción |
|------------|-------|-----|-----------|
| Estrategias | 10+ | 1 | 90% |
| Pares de trading | 50+ | 2 | 96% |
| Páginas frontend | 6 | 3 | 50% |
| Providers de auth | 3 | 1 | 67% |
| APIs externas | 5 | 1 | 80% |
| Base de datos | PostgreSQL | SQLite | N/A |
| Observabilidad | Stack completo | Básico | 80% |
| Configuraciones | 30+ | 8 | 73% |
| **Complejidad Total** | **100%** | **~25%** | **75%** |

---

## ⚠️ RIESGOS Y MITIGACIONES

### Riesgo 1: SQLite No Escala
**Mitigación:** Limitar MVP a 50 usuarios beta, migrar a Postgres si crece.

### Riesgo 2: Sin Encriptación de API Keys
**Mitigación:**
- Advertencia clara en UI
- Solo permitir API keys con permisos limitados (sin withdrawals)
- Roadmap: encriptación en v1.1

### Riesgo 3: Single Tenant = No Multi-Usuario Real
**Mitigación:**
- Deployment por usuario (cada uno su instancia)
- O multi-tenant suave (sin aislamiento estricto) con disclaimer

### Riesgo 4: Observabilidad Limitada
**Mitigación:**
- Monitoreo manual diario
- Health checks automáticos cada 5 min
- Alertas manuales vía Telegram/Email al admin

### Riesgo 5: Solo 2 Pares = Oportunidades Limitadas
**Mitigación:**
- BTC y ETH son los más líquidos y confiables
- Agregar más pares según demanda de usuarios

---

## 📅 ROADMAP POST-MVP

### v1.1 (Sprint 1 - 2 semanas)
- Encriptación de API keys
- Email verification
- 3 pares adicionales (BNB, SOL, ADA)
- Métricas avanzadas (Sharpe, Sortino)

### v1.2 (Sprint 2 - 1 mes)
- PostgreSQL migration
- Redis caching
- Telegram notifications
- Password reset con email

### v1.3 (Sprint 3 - 2 meses)
- ML-enhanced strategy
- Backtesting con UI
- Multi-usuario real (multi-tenant)
- OAuth providers (Google, GitHub)

### v2.0 (Q1 2026)
- Custom strategy builder
- Multiple exchanges
- Tax calculator
- Subscription model

---

## 🎯 DEFINICIÓN DE "DONE" PARA MVP

### Funcional ✅
- [x] Usuario puede registrarse y hacer login
- [x] Usuario puede configurar API keys Binance
- [x] Usuario puede activar paper trading
- [x] Dashboard muestra trades y métricas en tiempo real
- [x] Usuario puede ver posiciones abiertas
- [x] Sistema corre 24/7 sin crashear

### Técnico ✅
- [x] Health checks pasando
- [x] No errores 500 en flujo core
- [x] Latencia API <500ms P95
- [x] Frontend sin errores de consola
- [x] Tests críticos pasando (risk manager)

### Seguridad ✅
- [x] Authentication funcional
- [x] Rate limiting activo
- [x] CORS configurado
- [x] Solo paper trading habilitado (live trading require flag manual)

### Operación ✅
- [x] CI/CD básico funcionando
- [x] Deployment a staging exitoso
- [x] Smoke tests pasando
- [x] Plan de rollback documentado

---

## 📝 DOCUMENTACIÓN MVP

### Para Usuarios Beta
**README_MVP.md:**
- Qué funciona (y qué no) en MVP
- Cómo empezar (5 minutos)
- Limitaciones conocidas
- Cómo reportar bugs

### Para Desarrollo
**CONTRIBUTING_MVP.md:**
- Feature flags disponibles
- Cómo habilitar features experimentales
- Qué está aplazado y por qué
- Cómo agregar nuevas features post-MVP

---

## ✅ APROBACIÓN PARA LANZAMIENTO

**MVP está listo para producción cuando:**
1. ✅ Todos los items MUST HAVE implementados
2. ✅ Feature flags configurados correctamente
3. ✅ Smoke tests pasando en staging
4. ✅ Documentación MVP completa
5. ✅ Plan de rollback validado
6. ✅ Monitoreo básico activo
7. ✅ 0 errores críticos en flujo core

**Criterio de Éxito Post-Lanzamiento (Primeras 48h):**
- Uptime >99%
- 0 crasheos del backend
- ≥3 usuarios beta haciendo paper trading exitosamente
- 0 quejas de seguridad/pérdida de datos
- Latencias dentro de objetivos

---

**Versión del Documento:** 1.0
**Última Actualización:** 2025-11-10
**Responsable:** Claude Code
**Estado:** DRAFT - Pendiente Aprobación
