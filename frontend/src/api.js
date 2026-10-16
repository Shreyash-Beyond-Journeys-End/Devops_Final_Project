// all calls go to /api, nginx (or the vite dev server) sends them to the backend

async function request(url, options = {}) {
  let res;
  try {
    res = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (err) {
    throw new Error("Could not reach the API");
  }

  if (res.status === 422) {
    throw new Error("Company and role are required (max 120 characters)");
  }
  if (!res.ok) {
    throw new Error("Request failed (" + res.status + ")");
  }
  // delete returns 204 with no body
  if (res.status === 204) {
    return null;
  }
  return res.json();
}

export function getJobs(status) {
  if (status) {
    return request("/api/jobs?status=" + status);
  }
  return request("/api/jobs");
}

export function getStats() {
  return request("/api/jobs/stats");
}

export function addJob(job) {
  return request("/api/jobs", { method: "POST", body: JSON.stringify(job) });
}

export function updateJob(id, job) {
  return request("/api/jobs/" + id, { method: "PUT", body: JSON.stringify(job) });
}

export function deleteJob(id) {
  return request("/api/jobs/" + id, { method: "DELETE" });
}
