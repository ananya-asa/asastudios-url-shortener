const form = document.querySelector("#shorten-form");
const urlInput = document.querySelector("#long-url");
const button = document.querySelector("#generate-button");
const copyButton = document.querySelector("#copy-button");
const feedback = document.querySelector("#form-feedback");
const result = document.querySelector("#short-result");
const shortUrl = document.querySelector("#short-url");
const expiresAt = document.querySelector("#expires-at");

function showFeedback(message, isError = false) {
  feedback.textContent = message;
  feedback.classList.toggle("is-error", isError);
  feedback.hidden = false;
}

copyButton.addEventListener("click", async () => {
  const url = shortUrl.href;
  if (!url) return;

  try {
    await navigator.clipboard.writeText(url);
    copyButton.textContent = "Copied";
    copyButton.classList.add("is-copied");
    window.setTimeout(() => {
      copyButton.textContent = "Copy";
      copyButton.classList.remove("is-copied");
    }, 1200);
  } catch {
    showFeedback("Clipboard access was blocked. Copy the URL manually.");
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  feedback.hidden = true;
  feedback.classList.remove("is-error");
  button.disabled = true;
  button.classList.add("is-loading");
  button.textContent = "Generating";
  result.classList.remove("is-visible");
  try {
    const response = await fetch("/shorten", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ long_url: urlInput.value.trim() }),
    });
    if (response.status === 422) return showFeedback("That URL is about as valid as a fake Wi‑Fi name.", true);
    if (response.status === 429) return showFeedback("Too many links. The server needs a tiny coffee break.", true);
    if (!response.ok) return showFeedback("The link machine is having a dramatic exit. Try again.", true);
    const data = await response.json();
    shortUrl.href = data.short_url;
    shortUrl.textContent = data.short_url;
    const expiry = new Date(data.expires_at);
    expiresAt.dateTime = expiry.toISOString();
    expiresAt.textContent = new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(expiry);
    copyButton.textContent = "Copy";
    copyButton.classList.remove("is-copied");
    result.hidden = false;
    requestAnimationFrame(() => result.classList.add("is-visible"));
  } catch {
    showFeedback("Couldn't reach the server. Check your connection and try again.");
  } finally {
    button.disabled = false;
    button.classList.remove("is-loading");
    button.textContent = "Generate";
  }
});