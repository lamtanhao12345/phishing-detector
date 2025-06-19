async function predictPhishing(url) {
  try {
    const response = await fetch("http://localhost:5001/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });
    const data = await response.json();
    return {
      isPhishing: data.is_phishing,
      probability: data.probability,
      url: data.url
    };
  } catch (error) {
    console.error('Error fetching prediction:', error);
    return {
      isPhishing: false,
      probability: 0.5,
      url
    }; // Fallback if API fails
  }
}