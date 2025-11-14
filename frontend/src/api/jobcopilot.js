export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function uploadDocs(cvFile, transcriptFile) {
  const formData = new FormData();
  if (cvFile) formData.append("cv", cvFile);
  if (transcriptFile) formData.append("transcript", transcriptFile);
  formData.append("userId", "demo-user");

  const res = await fetch(`${API_BASE}/api/upload-docs`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function startWorkflow(message, language = "en", profile = null) {
  const userData = { language, userId: "demo-user" };
  if (profile) {
    userData.profile = profile;
  }

  const res = await fetch(`${API_BASE}/workflow/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_message: message,
      user_data: userData
    })
  });
  return res.json();
}

export async function getWorkflowStatus(workflowId) {
  const res = await fetch(`${API_BASE}/workflow/${workflowId}/status`);
  return res.json();
}

export async function submitApplication(job, userId = "demo-user") {
  const res = await fetch(`${API_BASE}/api/apply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job, userId })
  });
  if (!res.ok) throw new Error("Apply failed");
  return res.json();
}
