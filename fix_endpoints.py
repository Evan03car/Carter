#!/usr/bin/env python3
# Script to fix all remaining endpoints with dependency injection

import re

# Read the server.py file
with open('/app/backend/server.py', 'r') as f:
    content = f.read()

# Fix all remaining endpoints with dependency injection
fixes = [
    # Get saved items
    (r'@api_router\.get\("/saved-items"\)\nasync def get_saved_items\(\):\s*"""Get user\'s saved items"""\s*try:\s*user = await get_current_user\(\)',
     '@api_router.get("/saved-items")\nasync def get_saved_items(user: User = Depends(get_current_user)):\n    """Get user\'s saved items"""\n    try:'),
    
    # Delete saved item
    (r'@api_router\.delete\("/saved-items/\{item_id\}"\)\nasync def delete_saved_item\(item_id: str\):\s*"""Delete a saved item"""\s*try:\s*user = await get_current_user\(\)',
     '@api_router.delete("/saved-items/{item_id}")\nasync def delete_saved_item(item_id: str, user: User = Depends(get_current_user)):\n    """Delete a saved item"""\n    try:'),
    
    # Create deal alert
    (r'@api_router\.post\("/deal-alerts"\)\nasync def create_deal_alert\(alert: DealAlert\):\s*"""Create a deal alert"""\s*try:\s*user = await get_current_user\(\)',
     '@api_router.post("/deal-alerts")\nasync def create_deal_alert(alert: DealAlert, user: User = Depends(get_current_user)):\n    """Create a deal alert"""\n    try:'),
    
    # Get deal alerts
    (r'@api_router\.get\("/deal-alerts"\)\nasync def get_deal_alerts\(\):\s*"""Get user\'s deal alerts"""\s*try:\s*user = await get_current_user\(\)',
     '@api_router.get("/deal-alerts")\nasync def get_deal_alerts(user: User = Depends(get_current_user)):\n    """Get user\'s deal alerts"""\n    try:'),
    
    # Delete deal alert
    (r'@api_router\.delete\("/deal-alerts/\{alert_id\}"\)\nasync def delete_deal_alert\(alert_id: str\):\s*"""Delete a deal alert"""\s*try:\s*user = await get_current_user\(\)',
     '@api_router.delete("/deal-alerts/{alert_id}")\nasync def delete_deal_alert(alert_id: str, user: User = Depends(get_current_user)):\n    """Delete a deal alert"""\n    try:'),
    
    # Subscription checkout
    (r'@api_router\.post\("/subscriptions/checkout"\)\nasync def create_subscription_checkout\(request: Request\):\s*"""Create Stripe checkout for subscription"""\s*try:\s*user = await get_current_user\(\)',
     '@api_router.post("/subscriptions/checkout")\nasync def create_subscription_checkout(request: Request, user: User = Depends(get_current_user)):\n    """Create Stripe checkout for subscription"""\n    try:'),
    
    # Payment status
    (r'@api_router\.get\("/subscriptions/status/\{session_id\}"\)\nasync def check_payment_status\(session_id: str\):\s*"""Check payment status"""\s*try:\s*user = await get_current_user\(\)',
     '@api_router.get("/subscriptions/status/{session_id}")\nasync def check_payment_status(session_id: str, user: User = Depends(get_current_user)):\n    """Check payment status"""\n    try:'),
    
    # Dashboard
    (r'@api_router\.get\("/dashboard"\)\nasync def get_dashboard\(\):\s*"""Get dashboard data"""\s*try:\s*user = await get_current_user\(\)',
     '@api_router.get("/dashboard")\nasync def get_dashboard(user: User = Depends(get_current_user)):\n    """Get dashboard data"""\n    try:')
]

# Apply fixes
for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

# Write back the fixed content
with open('/app/backend/server.py', 'w') as f:
    f.write(content)

print('Fixed all dependency injection issues in server.py')