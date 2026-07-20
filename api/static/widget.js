/**
 * AI Portfolio Assistant - Widget Loader
 * Lightweight script that creates a floating chat bubble and iframe.
 *
 * Usage:
 *   <script src="https://app.yourdomain.com/widget.js" data-widget-id="abc123" async></script>
 *
 * Options (data attributes):
 *   data-widget-id   - Your widget ID (required)
 *   data-position    - bottom-right | bottom-left | top-right | top-left (default: bottom-right)
 *   data-greeting    - Custom greeting text
 */
(function () {
  var script = document.currentScript;
  if (!script) return;

  var widgetId = script.getAttribute("data-widget-id");
  if (!widgetId) {
    console.error("Portfolio Chat: data-widget-id is required");
    return;
  }

  var position = script.getAttribute("data-position") || "bottom-right";
  var greeting = script.getAttribute("data-greeting") || "";
  var baseUrl = script.src.replace(/\/widget\.js(\?.*)?$/, "");

  // Prevent double-loading
  if (window.__portfolioChatLoaded) return;
  window.__portfolioChatLoaded = true;

  // Inject styles
  var style = document.createElement("style");
  style.textContent =
    ".portfolio-chat-bubble{position:fixed;width:60px;height:60px;border-radius:50%;background:#4F46E5;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:999999;transition:transform 0.2s,border-radius 0.2s;}.portfolio-chat-bubble:hover{transform:scale(1.1);}.portfolio-chat-bubble.open{border-radius:12px;width:60px;height:60px;}.portfolio-chat-bubble.bottom-right{bottom:24px;right:24px;}.portfolio-chat-bubble.bottom-left{bottom:24px;left:24px;}.portfolio-chat-bubble.top-right{top:24px;right:24px;}.portfolio-chat-bubble.top-left{top:24px;left:24px;}.portfolio-chat-overlay{position:fixed;z-index:999998;transition:opacity 0.3s,transform 0.3s;opacity:0;pointer-events:none;}.portfolio-chat-overlay.open{opacity:1;pointer-events:auto;}.portfolio-chat-overlay iframe{border:none;width:100%;height:100%;}.portfolio-chat-overlay.bottom-right{bottom:96px;right:24px;width:380px;height:520px;}.portfolio-chat-overlay.bottom-left{bottom:96px;left:24px;width:380px;height:520px;}.portfolio-chat-overlay.top-right{top:96px;right:24px;width:380px;height:520px;}.portfolio-chat-overlay.top-left{top:96px;left:24px;width:380px;height:520px;}@media(max-width:480px){.portfolio-chat-overlay iframe{width:calc(100vw - 32px);height:calc(100vh - 120px);}.portfolio-chat-overlay{bottom:16px!important;top:16px!important;left:16px!important;right:16px!important;width:auto!important;height:auto!important;}}";
  document.head.appendChild(style);

  // Chat icon SVG
  var chatIcon =
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>';
  var closeIcon =
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';

  // Create bubble
  var bubble = document.createElement("div");
  bubble.className = "portfolio-chat-bubble " + position;
  bubble.innerHTML = chatIcon;
  bubble.setAttribute("role", "button");
  bubble.setAttribute("aria-label", "Open chat");
  document.body.appendChild(bubble);

  // Create overlay
  var overlay = document.createElement("div");
  overlay.className = "portfolio-chat-overlay " + position;
  var iframeSrc = baseUrl + "/widget/" + widgetId;
  if (greeting) iframeSrc += "?greeting=" + encodeURIComponent(greeting);
  overlay.innerHTML =
    '<iframe src="' + iframeSrc + '" title="Portfolio Chat"></iframe>';
  document.body.appendChild(overlay);

  // Toggle
  var isOpen = false;
  bubble.addEventListener("click", function () {
    isOpen = !isOpen;
    bubble.innerHTML = isOpen ? closeIcon : chatIcon;
    bubble.classList.toggle("open", isOpen);
    overlay.classList.toggle("open", isOpen);
    bubble.setAttribute("aria-label", isOpen ? "Close chat" : "Open chat");
  });

  // Close on escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && isOpen) {
      bubble.click();
    }
  });
})();
