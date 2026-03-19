import * as Device from 'expo-device';
import Constants from 'expo-constants';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from './api';

// Analytics Events
export const AnalyticsEvents = {
  // User Events
  USER_SIGNUP: 'user_signup',
  USER_LOGIN: 'user_login',
  USER_LOGOUT: 'user_logout',
  
  // Search Events
  SEARCH_PERFORMED: 'search_performed',
  SEARCH_RESULT_CLICKED: 'search_result_clicked',
  PRICE_ESTIMATION_REQUESTED: 'price_estimation_requested',
  
  // Item Events
  ITEM_SAVED: 'item_saved',
  ITEM_UNSAVED: 'item_unsaved',
  ITEM_SHARED: 'item_shared',
  
  // Deal Alerts
  ALERT_CREATED: 'alert_created',
  ALERT_DELETED: 'alert_deleted',
  NOTIFICATION_RECEIVED: 'notification_received',
  NOTIFICATION_OPENED: 'notification_opened',
  
  // Subscription Events
  SUBSCRIPTION_VIEWED: 'subscription_viewed',
  SUBSCRIPTION_CHECKOUT_STARTED: 'subscription_checkout_started',
  SUBSCRIPTION_COMPLETED: 'subscription_completed',
  SEARCH_PACK_PURCHASED: 'search_pack_purchased',
  
  // Chat Events
  CHAT_MESSAGE_SENT: 'chat_message_sent',
  CHAT_CONVERSATION_STARTED: 'chat_conversation_started',
  
  // Feedback Events
  FEEDBACK_SUBMITTED: 'feedback_submitted',
  FEEDBACK_UPVOTED: 'feedback_upvoted',
  
  // App Events
  APP_OPENED: 'app_opened',
  APP_BACKGROUNDED: 'app_backgrounded',
  SCREEN_VIEWED: 'screen_viewed',
  ONBOARDING_COMPLETED: 'onboarding_completed',
  
  // Error Events
  ERROR_OCCURRED: 'error_occurred',
  API_ERROR: 'api_error',
};

// User Properties
interface UserProperties {
  user_id?: string;
  subscription_tier?: string;
  signup_date?: string;
  total_searches?: number;
  total_saved_items?: number;
}

// Device Info
interface DeviceInfo {
  device_id: string;
  device_brand: string;
  device_model: string;
  device_name: string;
  os_name: string;
  os_version: string;
  app_version: string;
  platform: string;
}

class Analytics {
  private userId: string | null = null;
  private deviceInfo: DeviceInfo | null = null;
  private sessionId: string;
  private sessionStart: Date;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.sessionStart = new Date();
    this.initialize();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async initialize() {
    await this.collectDeviceInfo();
    this.logEvent(AnalyticsEvents.APP_OPENED, {
      session_id: this.sessionId,
      session_start: this.sessionStart.toISOString(),
    });
  }

  private async collectDeviceInfo(): Promise<void> {
    try {
      this.deviceInfo = {
        device_id: Constants.sessionId || 'unknown',
        device_brand: Device.brand || 'unknown',
        device_model: Device.modelName || 'unknown',
        device_name: Device.deviceName || 'unknown',
        os_name: Device.osName || 'unknown',
        os_version: Device.osVersion || 'unknown',
        app_version: Constants.expoConfig?.version || '1.0.0',
        platform: Device.osName || 'unknown',
      };
    } catch (error) {
      console.error('Error collecting device info:', error);
    }
  }

  setUserId(userId: string) {
    this.userId = userId;
  }

  async setUserProperties(properties: UserProperties) {
    try {
      await AsyncStorage.setItem('user_properties', JSON.stringify(properties));
    } catch (error) {
      console.error('Error setting user properties:', error);
    }
  }

  async logEvent(
    eventName: string,
    params?: Record<string, any>
  ): Promise<void> {
    try {
      const userProperties = await this.getUserProperties();
      
      const eventData = {
        event_name: eventName,
        timestamp: new Date().toISOString(),
        session_id: this.sessionId,
        user_id: this.userId,
        device_info: this.deviceInfo,
        user_properties: userProperties,
        params: params || {},
      };

      // Log to console in development
      if (__DEV__) {
        console.log('📊 Analytics Event:', eventName, params);
      }

      // Send to backend
      await this.sendToBackend(eventData);
      
      // Store locally for offline support
      await this.storeLocally(eventData);
    } catch (error) {
      console.error('Error logging event:', error);
    }
  }

  private async getUserProperties(): Promise<UserProperties | null> {
    try {
      const stored = await AsyncStorage.getItem('user_properties');
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      return null;
    }
  }

  private async sendToBackend(eventData: any): Promise<void> {
    try {
      await api.post('/analytics/events', eventData);
    } catch (error) {
      // Queue for retry if offline
      await this.queueForRetry(eventData);
    }
  }

  private async storeLocally(eventData: any): Promise<void> {
    try {
      const key = `analytics_event_${Date.now()}`;
      await AsyncStorage.setItem(key, JSON.stringify(eventData));
    } catch (error) {
      console.error('Error storing event locally:', error);
    }
  }

  private async queueForRetry(eventData: any): Promise<void> {
    try {
      const queue = await AsyncStorage.getItem('analytics_retry_queue');
      const queueData = queue ? JSON.parse(queue) : [];
      queueData.push(eventData);
      await AsyncStorage.setItem('analytics_retry_queue', JSON.stringify(queueData));
    } catch (error) {
      console.error('Error queuing event for retry:', error);
    }
  }

  async retryQueuedEvents(): Promise<void> {
    try {
      const queue = await AsyncStorage.getItem('analytics_retry_queue');
      if (!queue) return;

      const queueData = JSON.parse(queue);
      const failedEvents = [];

      for (const event of queueData) {
        try {
          await api.post('/analytics/events', event);
        } catch (error) {
          failedEvents.push(event);
        }
      }

      if (failedEvents.length > 0) {
        await AsyncStorage.setItem('analytics_retry_queue', JSON.stringify(failedEvents));
      } else {
        await AsyncStorage.removeItem('analytics_retry_queue');
      }
    } catch (error) {
      console.error('Error retrying queued events:', error);
    }
  }

  logScreenView(screenName: string, params?: Record<string, any>) {
    this.logEvent(AnalyticsEvents.SCREEN_VIEWED, {
      screen_name: screenName,
      ...params,
    });
  }

  logSearch(query: string, category?: string, resultsCount?: number) {
    this.logEvent(AnalyticsEvents.SEARCH_PERFORMED, {
      query,
      category,
      results_count: resultsCount,
    });
  }

  logItemAction(action: string, itemId: string, itemData?: any) {
    this.logEvent(action, {
      item_id: itemId,
      ...itemData,
    });
  }

  logSubscriptionEvent(event: string, plan?: string, amount?: number) {
    this.logEvent(event, {
      plan,
      amount,
      currency: 'USD',
    });
  }

  logError(error: Error, context?: string) {
    this.logEvent(AnalyticsEvents.ERROR_OCCURRED, {
      error_message: error.message,
      error_stack: error.stack,
      context,
    });
  }

  async getSessionDuration(): Promise<number> {
    const now = new Date();
    return now.getTime() - this.sessionStart.getTime();
  }

  async endSession() {
    const duration = await this.getSessionDuration();
    await this.logEvent(AnalyticsEvents.APP_BACKGROUNDED, {
      session_id: this.sessionId,
      session_duration: duration,
    });
    await this.retryQueuedEvents();
  }
}

// Export singleton instance
export const analytics = new Analytics();

// Helper functions
export const trackEvent = (eventName: string, params?: Record<string, any>) => {
  analytics.logEvent(eventName, params);
};

export const trackScreen = (screenName: string) => {
  analytics.logScreenView(screenName);
};

export const trackError = (error: Error, context?: string) => {
  analytics.logError(error, context);
};

export default analytics;
