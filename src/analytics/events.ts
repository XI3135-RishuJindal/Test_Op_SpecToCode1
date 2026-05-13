/* Analytics events registry and safe tracker with payment-related events removed.
   Ensures no analytics/logs with names containing "payment", "billing", "upgrade", or "subscribe" are emitted.
*/

export type EventName =
  | 'app_open'
  | 'nav_opened'
  | 'page_view'
  | 'settings_opened'
  | 'user_profile_updated'
  | 'user_security_updated'
  | 'notifications_changed'
  | 'integration_connected';

export const Events: Record<EventName, EventName> = {
  app_open: 'app_open',
  nav_opened: 'nav_opened',
  page_view: 'page_view',
  settings_opened: 'settings_opened',
  user_profile_updated: 'user_profile_updated',
  user_security_updated: 'user_security_updated',
  notifications_changed: 'notifications_changed',
  integration_connected: 'integration_connected',
};

const BLOCKED_EVENT_TERMS = /(payment|billing|upgrade|subscribe)/i;

/**
 * Tracks an analytics event. Any attempted event with blocked payment-related
 * terms will be ignored to satisfy "No payment analytics