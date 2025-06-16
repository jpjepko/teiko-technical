export async function fetchJson(endpoint) {
  try {
    const res = await fetch(endpoint);
    if (!res.ok) {
      throw new Error(`request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`failed to fetch ${endpoint}: `, err);
    return null;  // can throw err here instead
  }
}
