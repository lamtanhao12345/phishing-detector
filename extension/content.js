chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'phishingResult' || message.type === 'phishingError') {
    chrome.runtime.sendMessage({ action: 'showPopup' });
  }
});