# Carter App - Data Collection & Analytics

## Overview

Carter collects various types of data to provide core functionality, improve user experience, and optimize app performance. This document outlines all data collection capabilities.

---

## Data Collection Categories

### 1. User Account Data
**What We Collect:**
- Email address
- Full name
- Profile picture (from Google OAuth)
- User ID (generated)
- Account creation date
- Subscription tier and status

**Why We Collect It:**
- Authentication and account management
- Personalized user experience
- Subscription management
- Support and customer service

**Storage:**
- MongoDB database
- Encrypted in transit (HTTPS)
- Secured access controls

---

### 2. Search & Usage Data
**What We Collect:**
- Search queries
- Search timestamps
- Search categories
- Items viewed
- Items saved/unsaved
- Time spent on screens
- Button clicks and interactions

**Why We Collect It:**
- Improve search relevance
- Understand user preferences
- Optimize app performance
- Provide better recommendations

**Retention:** 90 days for analytics, indefinitely for user's own history

---

### 3. Location Data
**What We Collect:**
- Approximate location (city/state)
- Distance from deals
- Location permissions status

**Why We Collect It:**
- Show local deals nearby
- Filter results by distance
- Provide location-based alerts

**User Control:**
- Optional - can be disabled in device settings
- Only collected when permission granted
- Only used when actively using app (not background)

---

### 4. Device & Technical Data
**What We Collect:**
- Device model and brand
- Operating system version
- App version
- Screen size and resolution
- Device language
- Network type (WiFi/Cellular)
- Crash reports and error logs
- Performance metrics

**Why We Collect It:**
- Debug and fix issues
- Optimize for different devices
- Improve app stability
- Measure performance

**Automatic Collection:** Yes, for all users

---

### 5. Analytics Events
**Events We Track:**
- App opens and closes
- Screen views
- Feature usage
- Search performed
- Item interactions
- Subscription actions
- Error occurrences
- Session duration

**Data Included:**
- Event name
- Timestamp
- Session ID
- User ID (if logged in)
- Device info
- Custom parameters

**Purpose:**
- Understand feature adoption
- Identify popular workflows
- Detect usability issues
- Measure engagement

---

### 6. Purchase & Transaction Data
**What We Collect:**
- Subscription purchases
- Search pack purchases
- Transaction IDs
- Payment status
- Purchase dates and amounts

**Why We Collect It:**
- Process payments
- Manage subscriptions
- Provide receipts
- Prevent fraud
- Customer support

**Third-Party:** Stripe (PCI-compliant payment processor)

---

### 7. Communication Data
**What We Collect:**
- Chat messages between users
- Feedback submissions
- Support requests
- Feedback upvotes

**Why We Collect It:**
- Enable community features
- Improve app based on feedback
- Provide customer support
- Moderate content

**Retention:** Messages stored indefinitely, support tickets for 2 years

---

### 8. Marketplace Search Data
**What We Collect:**
- SerpApi search results
- AI price estimates (via Gemini)
- Profit calculations
- Deal alerts created

**Why We Collect It:**
- Provide core app functionality
- Cache results for performance
- Track trending items
- Send deal notifications

**Third-Party Services:**
- SerpApi (marketplace data)
- Google Gemini (AI estimates)

---

## Analytics Implementation

### Frontend Tracking

**Automatic Events:**
```typescript
- App opened
- App backgrounded
- Screen viewed
- Session duration
```

**Manual Events:**
```typescript
analytics.logEvent('search_performed', {
  query: 'headphones',
  category: 'electronics',
  results_count: 15
});

analytics.logEvent('subscription_completed', {
  plan: 'premium',
  amount: 40
});
```

### Backend Storage

All events stored in MongoDB:
```javascript
{
  event_name: "search_performed",
  timestamp: "2025-07-15T10:30:00Z",
  session_id: "session_abc123",
  user_id: "user_xyz789",
  device_info: {
    device_model: "iPhone 15 Pro",
    os_version: "iOS 17.2",
    app_version: "1.0.0"
  },
  params: {
    query: "headphones",
    category: "electronics"
  }
}
```

---

## Privacy Controls

### User Rights

**Access Your Data:**
- Request full data export
- View all collected information
- Download personal data

**Delete Your Data:**
- Delete account and all associated data
- Remove specific data points
- Opt out of analytics

**Control Collection:**
- Disable location tracking
- Opt out of personalized ads
- Limit data sharing

### Consent Management

**iOS 14.5+ App Tracking Transparency:**
```swift
// Request tracking permission
"Your data helps us provide personalized deal 
recommendations and improve app performance"

Options: [Allow Tracking] [Ask App Not to Track]
```

**GDPR Compliance:**
- Explicit consent required
- Clear purpose descriptions
- Easy opt-out mechanisms
- Data portability

**CCPA Compliance:**
- California residents can opt out
- "Do Not Sell My Personal Information"
- Data deletion requests honored

---

## Data Retention

| Data Type | Retention Period |
|-----------|------------------|
| Account Info | Until account deletion |
| Search History | 90 days |
| Analytics Events | 1 year |
| Chat Messages | Indefinite (user can delete) |
| Crash Reports | 90 days |
| Purchase History | 7 years (tax/legal requirements) |
| Feedback | Until deletion requested |

---

## Data Sharing

### We DO Share Data With:
1. **Google** - Authentication (OAuth), AI (Gemini)
2. **SerpApi** - Marketplace search queries
3. **Stripe** - Payment processing
4. **Expo** - Push notifications, crash reporting

### We DO NOT:
- Sell your data to third parties
- Share data with advertisers
- Use data for unrelated purposes
- Track you across other apps/websites

---

## Security Measures

**Encryption:**
- All data encrypted in transit (TLS/SSL)
- Database encryption at rest
- Secure API endpoints

**Access Controls:**
- Role-based permissions
- Audit logs
- Regular security reviews

**Compliance:**
- GDPR compliant
- CCPA compliant
- SOC 2 certified infrastructure
- Regular penetration testing

---

## Analytics Dashboard (Admin)

Admins can view aggregated analytics:
- Total users and growth
- Daily/monthly active users
- Feature usage statistics
- Search popularity
- Conversion funnel
- Retention rates
- Error rates

**No Individual Tracking:** Admins cannot view individual user behavior

---

## Opt-Out Instructions

### Disable Location:
1. iOS Settings → Privacy → Location Services → Carter → Never
2. Android Settings → Apps → Carter → Permissions → Location → Deny

### Limit Analytics:
1. Carter App → Profile → Settings → Privacy
2. Toggle "Share Analytics Data" to OFF

### Delete Account:
1. Carter App → Profile → Settings → Account
2. "Delete My Account"
3. Confirm deletion
4. All data permanently removed within 30 days

---

## Data Breach Protocol

In the event of a data breach:
1. Immediate investigation and containment
2. Notification to affected users within 72 hours
3. Full disclosure of compromised data
4. Free credit monitoring if financial data affected
5. Steps taken to prevent future breaches

---

## Contact for Privacy Concerns

**Data Protection Officer:**
- Email: privacy@carterapp.com
- Response time: Within 48 hours

**Data Requests:**
- Access request: privacy@carterapp.com
- Deletion request: privacy@carterapp.com
- Complaint: privacy@carterapp.com

---

## Changes to Data Collection

We will notify users of any material changes:
- In-app notification
- Email to registered users
- Updated privacy policy
- 30-day notice before implementation

---

## Third-Party Services

### Google (Authentication & AI)
- **Data Shared:** Email, name, profile picture
- **Purpose:** Account login, price estimation
- **Privacy Policy:** https://policies.google.com/privacy

### SerpApi (Marketplace Data)
- **Data Shared:** Search queries
- **Purpose:** Fetch marketplace listings
- **Privacy Policy:** https://serpapi.com/privacy

### Stripe (Payments)
- **Data Shared:** Payment info, transaction details
- **Purpose:** Process subscriptions and purchases
- **Privacy Policy:** https://stripe.com/privacy
- **PCI DSS Certified**

### Expo (Infrastructure)
- **Data Shared:** Device info, crash reports
- **Purpose:** App delivery, push notifications
- **Privacy Policy:** https://expo.dev/privacy

---

## Analytics Metrics Collected

### User Metrics:
- New signups
- Daily/Monthly active users
- Retention rate
- Churn rate
- Session duration
- Session frequency

### Feature Metrics:
- Search usage
- AI estimator usage
- Items saved
- Alerts created
- Chat messages sent
- Feedback submitted

### Business Metrics:
- Subscription conversions
- Revenue
- Trial-to-paid conversion
- Search pack sales
- Refund rate

### Performance Metrics:
- App load time
- API response time
- Crash rate
- Error rate
- Network failures

---

## Compliance Certifications

- ✅ GDPR (EU General Data Protection Regulation)
- ✅ CCPA (California Consumer Privacy Act)
- ✅ COPPA (Children's Online Privacy Protection Act)
- ✅ App Store Privacy Requirements
- ✅ Google Play Privacy & Security Requirements

---

## App Store Privacy Labels

### iOS App Store Privacy Nutrition Label:

**Data Used to Track You:**
- None

**Data Linked to You:**
- Contact Info (Email, Name)
- User Content (Photos, Messages, Feedback)
- Identifiers (User ID)
- Usage Data (Product Interaction, Search History)
- Purchases (Purchase History)
- Location (Approximate Location)

**Data Not Linked to You:**
- Diagnostics (Crash Data, Performance Data)

---

This data collection enables Carter to provide a personalized, high-quality experience while respecting your privacy and giving you control over your information.

Last Updated: 2025
