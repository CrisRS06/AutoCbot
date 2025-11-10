/**
 * Feature Flags for Frontend - MVP Configuration
 *
 * Controls which features are visible/enabled in the UI
 * Flags should match backend feature flags for consistency
 *
 * For MVP, most advanced features are disabled
 */

export interface FeatureFlags {
  // Trading Features
  enableLiveTrading: boolean;
  enablePaperTrading: boolean;
  enableSmartOrders: boolean;

  // Strategy Features
  enableMLStrategy: boolean;
  enableBacktest: boolean;
  enableStrategyCreation: boolean;

  // Analytics Features
  enableAdvancedMetrics: boolean;
  enablePerformanceCharts: boolean;
  enablePnLCharts: boolean;

  // Notification Features
  enableTelegram: boolean;
  enableEmailNotifications: boolean;
  enableWebhooks: boolean;

  // UI Features
  enableDarkMode: boolean;
  enableExport: boolean;
}

/**
 * Default feature flags for MVP
 * Only essential features are enabled
 */
const defaultFlags: FeatureFlags = {
  // Trading - Paper trading enabled, live trading disabled for MVP
  enableLiveTrading: false,
  enablePaperTrading: true,
  enableSmartOrders: true,

  // Strategy - Only viewing/using existing strategies, no ML or backtest
  enableMLStrategy: false,
  enableBacktest: false,
  enableStrategyCreation: false,

  // Analytics - Basic metrics only
  enableAdvancedMetrics: false,
  enablePerformanceCharts: true,
  enablePnLCharts: true,

  // Notifications - All disabled for MVP
  enableTelegram: false,
  enableEmailNotifications: false,
  enableWebhooks: false,

  // UI Features - Basic functionality
  enableDarkMode: true,
  enableExport: false,
};

/**
 * Load feature flags from environment variables
 * Falls back to defaults if env vars not set
 */
function loadFeatureFlags(): FeatureFlags {
  // For MVP, we use default flags
  // In production, these could be loaded from environment variables
  // or from a remote configuration service

  if (typeof window === 'undefined') {
    // Server-side rendering - use defaults
    return defaultFlags;
  }

  // Check if we have environment-specific overrides
  const envFlags = {
    enableLiveTrading: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_LIVE_TRADING', false),
    enablePaperTrading: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_PAPER_TRADING', true),
    enableSmartOrders: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_SMART_ORDERS', true),

    enableMLStrategy: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_ML_STRATEGY', false),
    enableBacktest: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_BACKTEST', false),
    enableStrategyCreation: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_STRATEGY_CREATION', false),

    enableAdvancedMetrics: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_ADVANCED_METRICS', false),
    enablePerformanceCharts: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_PERFORMANCE_CHARTS', true),
    enablePnLCharts: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_PNL_CHARTS', true),

    enableTelegram: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_TELEGRAM', false),
    enableEmailNotifications: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_EMAIL_NOTIFICATIONS', false),
    enableWebhooks: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_WEBHOOKS', false),

    enableDarkMode: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_DARK_MODE', true),
    enableExport: getEnvFlag('NEXT_PUBLIC_FEATURE_ENABLE_EXPORT', false),
  };

  return envFlags;
}

/**
 * Helper to get boolean flag from environment variable
 */
function getEnvFlag(key: string, defaultValue: boolean): boolean {
  if (typeof window === 'undefined') {
    return defaultValue;
  }

  const value = process.env[key];
  if (value === undefined) {
    return defaultValue;
  }

  return value === 'true' || value === '1';
}

/**
 * Global feature flags instance
 * Import this to check feature availability
 */
export const featureFlags: FeatureFlags = loadFeatureFlags();

/**
 * Utility functions for common flag checks
 */
export const canUseLiveTrading = (): boolean => featureFlags.enableLiveTrading;
export const canUsePaperTrading = (): boolean => featureFlags.enablePaperTrading;
export const canUseSmartOrders = (): boolean => featureFlags.enableSmartOrders;
export const canUseMLStrategy = (): boolean => featureFlags.enableMLStrategy;
export const canUseBacktest = (): boolean => featureFlags.enableBacktest;
export const canCreateStrategy = (): boolean => featureFlags.enableStrategyCreation;
export const canViewAdvancedMetrics = (): boolean => featureFlags.enableAdvancedMetrics;
export const canViewPerformanceCharts = (): boolean => featureFlags.enablePerformanceCharts;
export const canViewPnLCharts = (): boolean => featureFlags.enablePnLCharts;
export const canUseTelegram = (): boolean => featureFlags.enableTelegram;
export const canUseEmailNotifications = (): boolean => featureFlags.enableEmailNotifications;
export const canUseWebhooks = (): boolean => featureFlags.enableWebhooks;
export const canUseDarkMode = (): boolean => featureFlags.enableDarkMode;
export const canExport = (): boolean => featureFlags.enableExport;

/**
 * React hook for feature flags
 * Use this in components to conditionally render features
 *
 * Example:
 * ```tsx
 * import { useFeatureFlag } from '@/lib/featureFlags';
 *
 * function MyComponent() {
 *   const canBacktest = useFeatureFlag('enableBacktest');
 *
 *   return (
 *     <>
 *       {canBacktest && <BacktestButton />}
 *     </>
 *   );
 * }
 * ```
 */
export function useFeatureFlag(flag: keyof FeatureFlags): boolean {
  return featureFlags[flag];
}

/**
 * React component for conditional rendering based on feature flags
 *
 * Example:
 * ```tsx
 * import { FeatureGate } from '@/lib/featureFlags';
 *
 * function MyComponent() {
 *   return (
 *     <FeatureGate feature="enableBacktest">
 *       <BacktestPanel />
 *     </FeatureGate>
 *   );
 * }
 * ```
 */
export function FeatureGate({
  feature,
  children,
  fallback = null
}: {
  feature: keyof FeatureFlags;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  const isEnabled = featureFlags[feature];
  return <>{isEnabled ? children : fallback}</>;
}

/**
 * Debug helper - logs current feature flags to console
 * Only works in development mode
 */
export function debugFeatureFlags(): void {
  if (process.env.NODE_ENV === 'development') {
    console.group('🚩 Feature Flags (MVP Configuration)');
    console.table(featureFlags);
    console.groupEnd();
  }
}

// Auto-debug in development
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  debugFeatureFlags();
}
