
document.addEventListener('DOMContentLoaded', () => {
  const urlInput = document.getElementById('urlInput');
  const checkButton = document.getElementById('checkButton');
  const currentUrlButton = document.getElementById('currentUrlButton');
  const resultDiv = document.getElementById('result');
  const phishingStatus = document.getElementById('phishingStatus');
  const probability = document.getElementById('probability');
  const source = document.getElementById('source');
  const extraInfo = document.getElementById('extraInfo');
  const errorDiv = document.getElementById('error');

  // Lấy URL trang hiện tại
  currentUrlButton.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      urlInput.value = tabs[0].url;
      errorDiv.classList.add('hidden');
    });
  });

  // Kiểm tra URL
  checkButton.addEventListener('click', async () => {
    const url = urlInput.value.trim();
    if (!url) {
      errorDiv.textContent = 'Please enter a URL';
      errorDiv.classList.remove('hidden');
      resultDiv.classList.add('hidden');
      return;
    }

    try {
      errorDiv.classList.add('hidden');
      resultDiv.classList.add('hidden');

      const response = await fetch('http://localhost:5001/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url })
      });

      const data = await response.json();

      if (response.ok) {
        phishingStatus.textContent = data.is_phishing ? 'Phishing' : 'Safe';
        phishingStatus.className = data.is_phishing ? 'phishing' : 'safe';
        probability.textContent = (data.probability * 100).toFixed(2) + '%';
        source.textContent = data.source;

        // Hiển thị thông tin bổ sung từ PhishStats
        if (data.source === 'PhishStats' && data.first_seen) {
          extraInfo.innerHTML = `<strong>First Seen:</strong> ${data.first_seen}<br><strong>Details:</strong> ${JSON.stringify(data.details)}`;
          extraInfo.classList.remove('hidden');
        } else {
          extraInfo.classList.add('hidden');
        }

        resultDiv.classList.remove('hidden');
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (err) {
      errorDiv.textContent = `Error: ${err.message}`;
      errorDiv.classList.remove('hidden');
      resultDiv.classList.add('hidden');
    }
  });
});