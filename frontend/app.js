const form = document.querySelector("#shorten-form");
const urlInput = document.querySelector("#long-url");
const button = document.querySelector("#generate-button");
const feedback = document.querySelector("#form-feedback");
const result = document.querySelector("#short-result");
const shortUrl = document.querySelector("#short-url");
const expiresAt = document.querySelector("#expires-at");

function showFeedback(message) {
  feedback.textContent = message;
  feedback.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  feedback.hidden = true;
  button.disabled = true;
  button.textContent = "Generating";
  try {
    const response = await fetch("/shorten", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ long_url: urlInput.value.trim() }),
    });
    if (response.status === 422) return showFeedback("Enter a valid URL, including https://.");
    if (response.status === 429) return showFeedback("Slow down, try again shortly.");
    if (!response.ok) return showFeedback("Couldn't create that link. Try again shortly.");
    const data = await response.json();
    const path = new URL(data.short_url).pathname;
    shortUrl.href = `${window.location.origin}${path}`;
    shortUrl.textContent = shortUrl.href;
    const expiry = new Date(data.expires_at);
    expiresAt.dateTime = expiry.toISOString();
    expiresAt.textContent = new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(expiry);
    result.hidden = false;
  } catch {
    showFeedback("Couldn't reach the server. Check your connection and try again.");
  } finally {
    button.disabled = false;
    button.textContent = "Generate";
  }
});