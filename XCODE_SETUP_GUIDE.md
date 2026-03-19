# Carter iOS - Xcode Configuration Guide

## Prerequisites

Before opening in Xcode, you need to generate the native iOS project:

```bash
cd /app/frontend

# Pre-build the iOS project
npx expo prebuild --platform ios

# This creates the ios/ directory with Xcode project files
```

---

## Project Structure After Prebuild

```
frontend/
├── ios/
│   ├── Carter.xcodeproj/
│   ├── Carter.xcworkspace/      # Open this in Xcode
│   ├── Podfile
│   ├── Pods/
│   └── Carter/
│       ├── AppDelegate.swift
│       ├── Info.plist
│       └── Supporting/
└── ...
```

---

## Opening in Xcode

**IMPORTANT:** Always open the `.xcworkspace` file, NOT the `.xcodeproj` file!

```bash
cd /app/frontend/ios
open Carter.xcworkspace
```

Or from Xcode:
- File → Open → Navigate to `/app/frontend/ios/Carter.xcworkspace`

---

## Required Xcode Configuration

### 1. Signing & Capabilities

1. Select the **Carter** project in the navigator
2. Select the **Carter** target
3. Go to **Signing & Capabilities** tab
4. **Automatic Signing:**
   - Check "Automatically manage signing"
   - Select your Team (Apple Developer Account)
   - Bundle Identifier: `com.carter.app`

5. **Add Capabilities:**
   - Push Notifications
   - Background Modes → Remote notifications
   - App Tracking Transparency

### 2. Info.plist Privacy Descriptions

Already configured, but verify these exist:
- **NSCameraUsageDescription**: "Take photos to estimate item value"
- **NSPhotoLibraryUsageDescription**: "Choose photos to estimate resale prices"
- **NSLocationWhenInUseUsageDescription**: "Find local deals near you"
- **NSUserTrackingUsageDescription**: "Your data helps improve app recommendations"

### 3. Build Settings

**Key Settings to Verify:**

- **iOS Deployment Target**: 13.4 or higher
- **Swift Language Version**: Swift 5.0
- **Enable Bitcode**: NO (deprecated by Apple)
- **Dead Code Stripping**: YES
- **Strip Debug Symbols During Copy**: YES (Release only)

### 4. Schemes

Verify you have two schemes:
- **Carter (Debug)**: For development
- **Carter (Release)**: For TestFlight/App Store

---

## Installing CocoaPods Dependencies

```bash
cd /app/frontend/ios

# Install pods
pod install

# If you encounter issues:
pod deintegrate
pod install --repo-update
```

---

## Running on Simulator

### From Xcode:
1. Select a simulator (e.g., iPhone 15 Pro)
2. Click the Play button or press ⌘R
3. App will build and launch in simulator

### From Terminal:
```bash
# List available simulators
xcrun simctl list devices

# Boot a simulator
xcrun simctl boot "iPhone 15 Pro"

# Run the app
cd /app/frontend
npx expo run:ios
```

---

## Running on Physical Device

### Requirements:
- iPhone or iPad
- Lightning/USB-C cable
- Device registered in Apple Developer Portal
- Provisioning profile

### Steps:
1. Connect device via cable
2. Trust computer on device if prompted
3. In Xcode, select your device from the device menu
4. Click Run (⌘R)
5. On device: Settings → General → Device Management → Trust developer

---

## Building for TestFlight/App Store

### Method 1: Using Xcode

1. **Archive the App:**
   - Product → Archive
   - Wait for build to complete
   - Organizer window opens automatically

2. **Distribute:**
   - Select the archive
   - Click "Distribute App"
   - Choose "App Store Connect"
   - Follow prompts to upload

### Method 2: Using EAS (Recommended)

```bash
cd /app/frontend

# Build for App Store
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios
```

---

## Common Xcode Issues & Solutions

### Issue 1: "No signing certificate found"
**Solution:**
- Xcode → Preferences → Accounts
- Add your Apple ID
- Download Manual Profiles

### Issue 2: "Command PhaseScriptExecution failed"
**Solution:**
```bash
cd /app/frontend/ios
pod deintegrate
pod install
# Clean build folder in Xcode: Shift + ⌘K
```

### Issue 3: "Multiple commands produce..."
**Solution:**
- File → Project Settings → Build System → Legacy Build System

### Issue 4: Metro bundler not starting
**Solution:**
```bash
# Kill any running Metro instances
lsof -ti:8081 | xargs kill -9

# Start Metro manually
cd /app/frontend
npx expo start
```

### Issue 5: "Unable to boot simulator"
**Solution:**
```bash
# Reset simulator
xcrun simctl erase all
```

---

## Debugging in Xcode

### Breakpoints:
- Click line number to add breakpoint
- Green arrow = breakpoint enabled
- Debug menu for more options

### Console Logs:
- View → Debug Area → Activate Console (⌘⇧Y)
- Filter logs with search bar

### React Native Debugger:
- Shake device/simulator
- Select "Debug" from menu
- Opens Chrome debugger

---

## Performance Profiling

### Instruments:
1. Product → Profile (⌘I)
2. Choose template:
   - **Time Profiler**: CPU usage
   - **Allocations**: Memory usage
   - **Leaks**: Memory leaks
   - **Network**: Network requests

---

## App Size Optimization

### Reduce App Size:
1. Enable **App Thinning** (automatic)
2. Use **On-Demand Resources**
3. Compress assets
4. Remove unused code

### Check App Size:
- Organizer → Archives → Estimate Size
- Should be < 200MB for initial download

---

## Required Assets for Xcode

### App Icons (all required sizes):
- 20x20 @2x, @3x
- 29x29 @2x, @3x
- 40x40 @2x, @3x
- 60x60 @2x, @3x
- 1024x1024 (App Store)

Use Xcode's Asset Catalog:
- `ios/Carter/Images.xcassets/AppIcon.appiconset/`

### Launch Screen:
- Already configured via Expo splash screen
- Customize in `ios/Carter/LaunchScreen.storyboard`

---

## Xcode Version Requirements

- **Minimum**: Xcode 14.0
- **Recommended**: Xcode 15.x (latest)
- **macOS**: macOS Ventura 13.0 or later

```bash
# Check Xcode version
xcodebuild -version

# Update command line tools
xcode-select --install
```

---

## Building for Different Environments

### Debug Build:
```bash
# Fast builds, includes debug symbols
xcodebuild -workspace Carter.xcworkspace \
  -scheme Carter \
  -configuration Debug \
  -sdk iphonesimulator \
  -derivedDataPath build
```

### Release Build:
```bash
# Optimized, production-ready
xcodebuild -workspace Carter.xcworkspace \
  -scheme Carter \
  -configuration Release \
  -sdk iphoneos \
  -archivePath build/Carter.xcarchive \
  archive
```

---

## Continuous Integration (CI/CD)

### Fastlane Setup:
```bash
cd /app/frontend/ios
fastlane init

# Create Fastfile for automation
```

### GitHub Actions Example:
```yaml
name: iOS Build
on: [push]
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: yarn install
      - name: Build iOS
        run: npx expo prebuild --platform ios
      - name: Run Xcode Build
        run: xcodebuild -workspace ios/Carter.xcworkspace -scheme Carter -configuration Release
```

---

## App Store Submission Checklist

- [ ] Bundle ID matches: `com.carter.app`
- [ ] Version number updated in Info.plist
- [ ] Build number incremented
- [ ] All required icons present
- [ ] Launch screen configured
- [ ] Privacy descriptions complete
- [ ] App capabilities added
- [ ] Provisioning profile valid
- [ ] Archive builds successfully
- [ ] Validated in Organizer
- [ ] Uploaded to App Store Connect
- [ ] Screenshots uploaded
- [ ] App description complete
- [ ] Age rating set
- [ ] Pricing configured

---

## Helpful Xcode Shortcuts

- **⌘B**: Build
- **⌘R**: Run
- **⌘.**: Stop
- **⌘⇧K**: Clean Build Folder
- **⌘⇧Y**: Toggle Debug Area
- **⌘⌥0**: Toggle Navigator
- **⌘0**: Show/Hide Navigator
- **⌘⌥⇧K**: Clean Derived Data
- **⌘I**: Profile (Instruments)

---

## Resources

- **Xcode Documentation**: https://developer.apple.com/xcode/
- **Expo Native Projects**: https://docs.expo.dev/workflow/customizing/
- **React Native iOS Guide**: https://reactnative.dev/docs/running-on-device
- **App Store Review Guidelines**: https://developer.apple.com/app-store/review/guidelines/

---

## Support

For Xcode-specific issues:
- Apple Developer Forums: https://developer.apple.com/forums/
- Stack Overflow: Tag `xcode` + `react-native`
- Expo Discord: #ios channel

For Carter app issues:
- Check `/app/DEPLOYMENT_GUIDE.md`
- Review error logs in Xcode console
- Test on multiple iOS versions

---

Your Carter app is configured and ready to run in Xcode! 🚀
