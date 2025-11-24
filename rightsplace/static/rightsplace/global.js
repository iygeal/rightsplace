// ======================================================================
// Global helper functions shared across RightsPlace pages.
// ======================================================================

// Debug helper: Log with consistent prefix
function rpLog(message, ...args) {
  console.log('[RightsPlace]', message, ...args);
}

// Smooth scroll to the top
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

