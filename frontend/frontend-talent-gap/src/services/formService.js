// Simple frontend service helper to submit the form payload.
// Adjust the API endpoint to match your backend route.

export const API_ENDPOINT = '/api/form';

export async function submitForm(payload) {
  const res = await fetch(API_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => null);
    let message = `Request failed: ${res.status}`;
    try {
      const json = JSON.parse(text);
      message = json.message || message;
    } catch (e) {
      if (text) message = text;
    }
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }

  // try to return parsed json when available
  try {
    return await res.json();
  } catch (e) {
    return null;
  }
}

export default { submitForm };
