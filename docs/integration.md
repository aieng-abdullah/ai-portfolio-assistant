# Integration Guide

## Quick Start (30 seconds)

1. Sign up at your domain
2. Fill in your profile + customize your widget
3. Copy your embed code
4. Paste it before `</body>` on your website
5. Done! A chat bubble appears on your site.

## Your Embed Code

```html
<script
  src="https://app.yourdomain.com/widget.js"
  data-widget-id="YOUR_WIDGET_ID"
  async
></script>
```

## Platform-Specific Instructions

### HTML / Static Sites
Paste the embed code before `</body>` in your HTML file.

```html
<!DOCTYPE html>
<html>
<head>...</head>
<body>
  <!-- Your content -->

  <script src="https://app.yourdomain.com/widget.js" data-widget-id="abc123" async></script>
</body>
</html>
```

### WordPress
**Method 1: Theme Editor**
1. Go to Appearance → Theme Editor
2. Open `footer.php`
3. Paste the embed code before `</body>`
4. Save

**Method 2: Plugin**
1. Install "Insert Headers and Footers" plugin
2. Go to Settings → Insert Headers and Footers
3. Paste in the "Scripts in Footer" section
4. Save

### Webflow
1. Go to Project Settings → Custom Code
2. Paste in "Footer Code"
3. Click Save & Publish

### Squarespace
1. Go to Settings → Advanced → Code Injection
2. Paste in the "Footer" section
3. Click Save

### Wix
1. Go to Settings → Custom Code → Add Code
2. Select "Body (End)"
3. Paste the embed code
4. Click Publish

### Shopify
1. Go to Online Store → Themes → Edit Code
2. Open `theme.liquid`
3. Paste before `</body>`
4. Save

### Next.js / React
```jsx
// In _app.js or layout.js
useEffect(() => {
  const script = document.createElement('script');
  script.src = 'https://app.yourdomain.com/widget.js';
  script.setAttribute('data-widget-id', 'abc123');
  script.async = true;
  document.body.appendChild(script);
}, []);
```

### Vue / Nuxt
```javascript
// In nuxt.config.js
export default {
  script: [
    { src: 'https://app.yourdomain.com/widget.js', 'data-widget-id': 'abc123', async: true }
  ]
}
```

## Widget Options

| Attribute | Description | Default |
|-----------|-------------|---------|
| `data-widget-id` | Your widget ID (required) | — |
| `data-position` | Position on screen | `bottom-right` |
| `data-greeting` | Custom greeting text | From dashboard |

### Position Options
- `bottom-right` (default)
- `bottom-left`
- `top-right`
- `top-left`

## Customization

All customization is done through the dashboard:
- Colors (primary, secondary)
- Font family
- Border radius
- Logo
- Chat title & subtitle
- Welcome message
- AI personality (Professional → Witty → Casual)
- Custom system prompt (advanced)

Changes apply instantly — no need to re-embed.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Widget not appearing | Check browser console for errors, verify script tag is correct |
| Chat not responding | Check if widget is active in dashboard |
| Styling conflicts | Widget runs in isolated iframe, shouldn't conflict |
| Mobile not showing | Widget is mobile responsive by default |
| "Chat unavailable" | Widget may be disabled — check dashboard |

## Testing

Test your widget at: `https://app.yourdomain.com/widget/YOUR_WIDGET_ID`
