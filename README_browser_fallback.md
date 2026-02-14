# Kalshi Browser Automation Fallback

This is a browser automation backup system for Kalshi trading when the API fails.

## Files Created

1. **`kalshi_browser_automation.js`** - Main automation script
2. **`kalshi_config.json`** - Configuration template (update with credentials)
3. **`test_kalshi_workflow.js`** - Test script demonstrating workflow
4. **`README_browser_fallback.md`** - This file

## Prerequisites

1. **Chrome Extension**: OpenClaw Browser Relay must be installed and active
2. **Attached Tab**: User must click the OpenClaw toolbar icon on a Chrome tab
3. **Credentials**: Kalshi username/password (update in config)

## Setup Instructions

### 1. Configure Credentials
```bash
# Edit the config file with your actual credentials
# Use environment variables for security in production
export KALSHI_USERNAME="your_email@example.com"
export KALSHI_PASSWORD="your_password"
```

### 2. Prepare Browser
1. Open Chrome with OpenClaw extension installed
2. Navigate to https://kalshi.com
3. Click the OpenClaw toolbar icon (badge should turn ON)
4. The tab is now attached and ready for automation

### 3. Test Navigation (Dry Run)
```javascript
// Use browser tool to test basic navigation
browser open https://kalshi.com
browser snapshot  // Check page loaded correctly
```

## Workflow Steps

The automation follows this sequence:

1. **Navigate to kalshi.com** - Load homepage
2. **Login** - Enter credentials and submit
3. **Find top 3 markets** - Identify market cards on page
4. **Execute trades** - For each market:
   - Click market detail
   - Click Yes/No button
   - Enter random amount ($1-2)
   - Submit trade
   - Capture confirmation screenshot
5. **Capture portfolio** - Take screenshot of portfolio page
6. **Generate report** - Log all trades executed

## Safety Features

- **Screenshots**: Every step captured for verification
- **Error handling**: Graceful failure with error screenshots
- **Timeout controls**: Prevents hanging on failed elements
- **Configurable amounts**: $1-2 minimum to limit risk
- **Dry run capability**: Can test without executing trades

## Usage with Browser Tool

```javascript
// Example commands for manual control
browser open https://kalshi.com
browser snapshot refs="aria"  // Get element references
browser act click ref="login-button"
browser act type ref="username-input" text="email@example.com"
browser act type ref="password-input" text="password123"
browser act click ref="submit-button"
browser screenshot  // Capture result
```

## Integration with API Failure Detection

When the main trading system detects API failure:

1. Switch to browser automation mode
2. Load credentials from secure storage
3. Execute `kalshi_browser_automation.js`
4. Monitor screenshots for confirmation
5. Resume API trading when restored

## Selector Maintenance

Kalshi may update their UI. If automation fails:

1. Check current page with `browser snapshot`
2. Update selectors in `kalshi_config.json`
3. Common changes:
   - Login button text/position
   - Market card structure
   - Trade modal layout

## Testing

Before relying on this fallback:

1. **Test login** - Verify credentials work
2. **Test navigation** - Ensure all pages load
3. **Test market identification** - Confirm top markets can be found
4. **Test trade flow** - Use minimum amounts ($0.01 if available)
5. **Test error recovery** - Simulate failed steps

## Security Notes

- Never commit credentials to version control
- Use environment variables in production
- Store screenshots securely (may contain sensitive info)
- Consider 2FA implications (may require manual intervention)

## Emergency Activation

When API fails and manual intervention needed:

```bash
# Quick start command
node -e "
const { KalshiBrowserAutomation } = require('./kalshi_browser_automation.js');
const playwright = require('playwright');

(async () => {
  const browser = await playwright.chromium.launch({ headless: false });
  const page = await browser.newPage();
  const automation = new KalshiBrowserAutomation(page);
  await automation.runFullWorkflow();
  await browser.close();
})();
"
```

## Status

✅ **Scripts created** - Ready for configuration
🔲 **Credentials configured** - Need user input
🔲 **Browser attached** - Need user to attach tab
🔲 **Selectors validated** - Need dry-run test
🔲 **Integration tested** - Need API failure simulation

This fallback system ensures trading can continue even if the Kalshi API experiences downtime.