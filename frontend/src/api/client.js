export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'https://sust-queuestorm-investigator.vercel.app').replace(/\/$/, '');

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    const message = typeof data === 'string' ? data : data?.detail || `Request failed with ${response.status}`;
    const error = new Error(message);
    error.status = response.status;
    error.payload = data;
    throw error;
  }
  return data;
}

export async function checkHealth(baseUrl = API_BASE_URL) {
  const response = await fetch(`${baseUrl.replace(/\/$/, '')}/health`, {
    method: 'GET',
    headers: { Accept: 'application/json' }
  });
  return parseResponse(response);
}

export async function analyzeTicket(payload, baseUrl = API_BASE_URL) {
  const response = await fetch(`${baseUrl.replace(/\/$/, '')}/analyze-ticket`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json'
    },
    body: JSON.stringify(payload)
  });
  return parseResponse(response);
}
