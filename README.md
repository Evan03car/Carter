# Profit Hunter - Resale Arbitrage Finder Mobile App

A professional mobile application (iOS/Android) that helps resellers find underpriced items on marketplaces to resell for profit.

## Features

### Core Functionality
- **Multi-Marketplace Search**: Scan eBay, Facebook Marketplace, Mercari, Poshmark, and Craigslist via SerpApi
- **AI Price Estimation**: Google Gemini-powered price analysis from images or listing links
- **Profit Calculator**: Automatic calculation including platform fees, shipping costs, and profit margins
- **Deal Alerts**: Push notifications for underpriced items in specific categories
- **Location-Based**: Find local pickup deals near you
- **Trending Items**: Track high-margin products across platforms
- **Saved Items**: Bookmark deals for later review

### Subscription Tiers
- **Free Trial**: 7 days free, 10 searches/day
- **Basic Plan**: $15/month, 50 searches/day
- **Premium Plan**: $40/month, unlimited searches + priority alerts

### Technology Stack

**Frontend (Mobile)**
- React Native with Expo
- TypeScript
- Expo Router (file-based routing)
- React Navigation (bottom tabs)
- Axios for API calls
- Expo Location, Notifications, Image Picker

**Backend**
- FastAPI (Python)
- MongoDB (AsyncIO Motor)
- Google Gemini AI (via Emergent LLM Key)
- SerpApi for marketplace data
- Stripe for payments
- Emergent Auth for Google OAuth

**Integrations**
- Emergent Google Authentication
- Google Gemini (gemini-2.5-pro & gemini-2.5-flash)
- SerpApi for marketplace scraping
- Stripe Checkout for subscriptions
- Expo Push Notifications

## Project Structure

```
/app
├── backend/
│   ├── server.py           # FastAPI server with all endpoints
│   ├── .env                # Environment variables
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── (tabs)/         # Tab navigation screens
│   │   │   ├── index.tsx   # Home/Dashboard
│   │   │   ├── search.tsx  # Marketplace search
│   │   │   ├── saved.tsx   # Saved items
│   │   │   └── profile.tsx # User profile
│   │   ├── _layout.tsx     # Root layout with AuthProvider
│   │   ├── index.tsx       # Landing page
│   │   └── auth-callback.tsx
│   ├── components/
│   │   └── DealCard.tsx    # Deal display component
│   ├── contexts/
│   │   └── AuthContext.tsx # Authentication context
│   ├── utils/
│   │   └── api.ts          # API client
│   ├── app.json            # Expo configuration
│   └── package.json
└── test_result.md          # Testing documentation
```

## API Endpoints

### Authentication
- `POST /api/auth/session` - Exchange session_id for session_token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user

### Marketplace Search
- `POST /api/search` - Search marketplaces for items
  - Body: `{ query, category?, max_price? }`
  - Returns: List of items with profit calculations

### Price Estimation
- `POST /api/estimate-price` - AI-powered price estimation
  - Body: `{ listing_url?, image_base64?, title?, description? }`
  - Returns: Estimated price, confidence, demand level, best platform

### Saved Items
- `POST /api/saved-items` - Save an item
- `GET /api/saved-items` - Get saved items
- `DELETE /api/saved-items/{item_id}` - Delete saved item

### Deal Alerts
- `POST /api/deal-alerts` - Create deal alert
- `GET /api/deal-alerts` - Get user's alerts
- `DELETE /api/deal-alerts/{alert_id}` - Delete alert

### Subscriptions
- `POST /api/subscriptions/checkout` - Create Stripe checkout session
- `GET /api/subscriptions/status/{session_id}` - Check payment status
- `POST /api/webhook/stripe` - Stripe webhook handler

### Dashboard
- `GET /api/dashboard` - Get dashboard stats and user info

## Environment Variables

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
EMERGENT_LLM_KEY=sk-emergent-...
SERPAPI_API_KEY=your_serpapi_key
STRIPE_API_KEY=sk_test_emergent
```

### Frontend (.env)
```
EXPO_PUBLIC_BACKEND_URL=https://your-app.preview.emergentagent.com
```

## Database Collections

- **users**: User profiles and subscription info
- **user_sessions**: Authentication sessions
- **saved_items**: Bookmarked deals
- **deal_alerts**: User alert preferences
- **payment_transactions**: Stripe payment records

## Setup & Installation

### Backend
```bash
cd /app/backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend
```bash
cd /app/frontend
yarn install
yarn start
```

## Testing

### Backend Testing
```bash
# Test API availability
curl http://localhost:8001/api/

# Test search (requires auth)
curl -X POST http://localhost:8001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "wireless headphones"}'
```

### Frontend Testing
- Use the `deep_testing_backend_v2` tool for backend API testing
- Use the `expo_frontend_testing_agent` tool for UI testing

## Key Features Implementation

### 1. Marketplace Search
- Uses SerpApi to query eBay (expandable to other platforms)
- AI estimates resale price using Gemini
- Calculates profit margins with platform fees
- Filters for minimum 15% profit margin

### 2. AI Price Estimation
- Supports image upload (base64) or listing URL
- Powered by Google Gemini 2.5 Pro
- Returns price, confidence level, demand, and best platform

### 3. Profit Calculator
- Platform-specific fee calculation
- Shipping cost estimation
- Net profit and margin percentage
- Real-time calculations

### 4. Subscription Management
- Stripe Checkout integration
- Automatic trial expiration handling
- Usage limits per tier
- Webhook-based payment verification

### 5. Authentication
- Emergent Google OAuth
- Session-based auth with cookies
- 7-day session expiration
- Protected API endpoints

## Mobile App Permissions

### iOS (Info.plist)
- NSCameraUsageDescription: "Take photos to estimate item value"
- NSPhotoLibraryUsageDescription: "Choose photos to estimate resale prices"
- NSLocationWhenInUseUsageDescription: "Find local deals near you"

### Android (permissions)
- CAMERA
- READ_EXTERNAL_STORAGE
- WRITE_EXTERNAL_STORAGE
- ACCESS_FINE_LOCATION
- ACCESS_COARSE_LOCATION

## Deployment Notes

- Backend runs on port 8001
- Frontend uses Expo tunnel for preview
- MongoDB runs locally on port 27017
- All API routes must be prefixed with `/api`
- Uses Kubernetes ingress routing

## Future Enhancements

1. Real-time price tracking
2. Historical price data
3. Multiple marketplace integration
4. Advanced analytics dashboard
5. Social features (share deals)
6. Browser extension
7. Barcode scanning
8. Voice search

## Support

For issues or questions, refer to the testing documentation in `test_result.md`.

## Version

1.0.0 - Initial Release

---

Built with ❤️ using Expo, FastAPI, and AI
