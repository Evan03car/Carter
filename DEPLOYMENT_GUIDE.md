# Carter - Native Deployment Guide

## Prerequisites

1. **Expo Account**: Sign up at https://expo.dev
2. **EAS CLI**: Install with `npm install -g eas-cli`
3. **Apple Developer Account** (for iOS): $99/year
4. **Google Play Developer Account** (for Android): $25 one-time

---

## Step 1: Configure EAS Project

```bash
cd /app/frontend

# Login to Expo
eas login

# Initialize EAS project
eas init

# This will create a project ID and update your app.json
```

---

## Step 2: Environment Variables for Production

Create `.env.production`:
```env
EXPO_PUBLIC_BACKEND_URL=https://your-production-api.com
```

Update your backend URL in production builds.

---

## Step 3: Build for iOS

### Configure iOS Bundle ID
Already set in `app.json`: `com.carter.app`

### Build iOS App
```bash
# Build for App Store (requires Apple Developer account)
eas build --platform ios --profile production

# Build for internal testing (no account needed)
eas build --platform ios --profile preview
```

### What you'll need:
- Apple Developer Team ID
- App Store Connect App ID
- Distribution certificate (EAS handles this automatically)

---

## Step 4: Build for Android

### Configure Android Package
Already set in `app.json`: `com.carter.app`

### Build Android APK/AAB
```bash
# Build APK for testing
eas build --platform android --profile preview

# Build AAB for Google Play Store
eas build --platform android --profile production
```

### For Google Play:
- Create app listing at https://play.google.com/console
- Upload AAB file
- Fill out store listing (screenshots, description, etc.)

---

## Step 5: App Store Listings

### iOS App Store Requirements

**Screenshots needed:**
- 6.7" iPhone (1290 x 2796) - iPhone 14 Pro Max
- 6.5" iPhone (1284 x 2778) - iPhone 11 Pro Max
- 5.5" iPhone (1242 x 2208) - iPhone 8 Plus
- 12.9" iPad Pro (2048 x 2732)

**App Information:**
- App Name: Carter
- Subtitle: Find Underpriced Resale Items
- Description: (See below)
- Keywords: resale, arbitrage, profit, flipping, deals, marketplace
- Category: Shopping / Business
- Age Rating: 4+

**Support URL**: Your website/support page
**Privacy Policy URL**: Required

### Android Play Store Requirements

**Screenshots needed:**
- Phone (16:9): 1080 x 1920
- 7-inch Tablet: 1024 x 600
- 10-inch Tablet: 1280 x 800

**App Information:**
- App Name: Carter
- Short Description: Find profitable resale deals with AI
- Full Description: (See below)
- Category: Shopping
- Content Rating: Everyone

---

## App Description Template

### Short Description (80 chars)
"Find underpriced items to resell for profit using AI-powered price estimation"

### Full Description
```
Carter helps resellers and flippers discover profitable arbitrage opportunities across multiple online marketplaces.

🔍 SMART MARKETPLACE SCANNING
• Search eBay, Facebook Marketplace, Mercari, Poshmark, and Craigslist
• Real-time price comparisons across platforms
• Find underpriced items instantly

🤖 AI-POWERED PRICE ESTIMATION
• Upload photos or paste listing links
• Get instant resale value estimates using Google Gemini AI
• Know exactly what items are worth

💰 PROFIT CALCULATOR
• See real profit margins
• Platform fees included automatically
• Shipping cost estimates
• Know your net profit before buying

🔔 DEAL ALERTS
• Get notified about profitable items
• Custom alerts by category
• Location-based deals near you
• Never miss a great opportunity

💬 COMMUNITY CHAT
• Connect with other resellers
• Share tips and strategies
• Build your network
• Learn from experienced flippers

📊 SUBSCRIPTION PLANS
• 5-Day Free Trial
• Basic: $12/month - 10 searches/day
• Premium: $40/month - 300 searches/day
• Buy search packs: 10 for $5, 25 for $7

Start finding profitable deals today with Carter!
```

---

## Step 6: App Privacy & Compliance

### Privacy Policy Required Disclosures

**Data Collected:**
- Email address (for authentication)
- Name and profile picture (Google OAuth)
- Search history (to improve recommendations)
- Location (for local deals - optional)
- Device info (for analytics)
- Purchase history (for subscription management)

**Data Usage:**
- Authentication and account management
- Provide core app functionality
- Process payments
- Send notifications about deals
- Improve user experience

**Third-Party Services:**
- Google OAuth (authentication)
- Google Gemini (AI price estimation)
- SerpApi (marketplace data)
- Stripe (payment processing)
- Expo Push Notifications

### Terms of Service
Include:
- Acceptable use policy
- Subscription terms (5-day trial, auto-renewal)
- Refund policy
- Liability disclaimer
- Age restrictions (13+)

---

## Step 7: Submit to Stores

### iOS App Store Submission
```bash
# Submit to TestFlight first
eas submit --platform ios --profile production

# Then submit for review via App Store Connect
```

**Review Process:**
- Typically 24-48 hours
- May request additional info
- Be ready to respond to review notes

### Google Play Store Submission
```bash
# Submit to internal testing first
eas submit --platform android --profile production
```

**Review Process:**
- Usually faster than iOS (hours to 1 day)
- May go through multiple reviews
- Start with internal testing track

---

## Step 8: Post-Launch Updates

### Over-The-Air (OTA) Updates
```bash
# Publish updates without resubmitting to stores
eas update --branch production --message "Bug fixes and improvements"
```

**Note:** OTA updates work for JS/React Native code changes only. Native changes require new builds.

### Version Management
```bash
# Increment version before new builds
# Update in app.json:
# - version: "1.0.1" (for App Store display)
# - ios.buildNumber: "2" (for iOS)
# - android.versionCode: 2 (for Android)
```

---

## Step 9: Required Assets

Create these image assets:

### App Icon (1024x1024)
- Place in: `assets/images/icon.png`
- Must be square with no transparency
- Will be auto-resized for all platforms

### Splash Screen (2048x2048 recommended)
- Place in: `assets/images/splash-icon.png`
- Centered logo on solid background
- Background color: #3B82F6 (Carter blue)

### Notification Icon (Android)
- Place in: `assets/images/notification-icon.png`
- 96x96, white icon on transparent background

---

## Step 10: Testing Before Launch

### Internal Testing
```bash
# Build preview version
eas build --platform all --profile preview

# Share with testers via:
# - TestFlight (iOS)
# - Internal testing track (Android)
```

### What to Test:
- ✅ Authentication flow
- ✅ Marketplace search
- ✅ AI price estimation (upload image)
- ✅ Profit calculator
- ✅ Save/unsave items
- ✅ Deal alerts
- ✅ Chat functionality
- ✅ Feedback submission
- ✅ Subscription purchase flow
- ✅ Search pack purchase
- ✅ Push notifications
- ✅ Location permissions
- ✅ Camera/photo permissions

---

## Common Issues & Solutions

### Issue: Build fails on iOS
**Solution:** Check Apple Developer account status and certificates

### Issue: App crashes on launch
**Solution:** Check environment variables are properly set

### Issue: Push notifications not working
**Solution:** Verify Expo push notification credentials are configured

### Issue: "This app is not available in your country"
**Solution:** Configure availability in App Store Connect / Play Console

---

## Production Checklist

- [ ] Environment variables configured for production
- [ ] Backend API deployed and accessible
- [ ] Database connection secure (SSL)
- [ ] API keys secured (not hardcoded)
- [ ] Privacy policy hosted and linked
- [ ] Terms of service hosted and linked
- [ ] Support email/contact setup
- [ ] App icons created (1024x1024)
- [ ] Screenshots taken for all required sizes
- [ ] App Store/Play Store descriptions written
- [ ] Stripe configured for production
- [ ] Push notifications tested
- [ ] All permissions justified and working
- [ ] Version numbers updated
- [ ] Beta testing completed
- [ ] Crash reporting setup (Sentry/Bugsnag)

---

## Monitoring & Analytics

### Recommended Tools:
- **Expo Application Services (EAS)**: Build and deployment
- **Sentry**: Crash reporting
- **Google Analytics / Firebase**: User analytics
- **App Store Connect / Play Console**: Download metrics
- **Stripe Dashboard**: Subscription metrics

---

## Support & Resources

- **Expo Documentation**: https://docs.expo.dev
- **EAS Build**: https://docs.expo.dev/build/introduction/
- **App Store Guidelines**: https://developer.apple.com/app-store/review/guidelines/
- **Play Store Guidelines**: https://play.google.com/about/developer-content-policy/

---

## Quick Commands Reference

```bash
# Login to EAS
eas login

# Create build
eas build --platform ios --profile production
eas build --platform android --profile production

# Submit to stores
eas submit --platform ios
eas submit --platform android

# Publish OTA update
eas update --branch production --message "Your update message"

# View build status
eas build:list

# View project info
eas project:info
```

---

## Estimated Timeline

- **Setup & Configuration**: 1-2 days
- **Asset Creation** (icons, screenshots): 1-2 days
- **Store Listings**: 1 day
- **Testing**: 2-3 days
- **iOS Review**: 2-7 days
- **Android Review**: 1-3 days

**Total: ~2 weeks from start to published**

---

For questions or issues, refer to Expo documentation or the Carter development team.
