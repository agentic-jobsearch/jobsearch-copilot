const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function uploadDocs(cvFile, transcriptFile) {
  const formData = new FormData();
  if (cvFile) formData.append("cv", cvFile);
  if (transcriptFile) formData.append("transcript", transcriptFile);
  formData.append("userId", "demo-user");

  const res = await fetch(`${API_BASE}/workflow/upload`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function startWorkflow(message, language = "en") {
  const res = await fetch(`${API_BASE}/workflow/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_input: message,
      user_data: { language, userId: "demo-user" }
    })
  });
  return res.json();
}

export async function getWorkflowStatus(workflowId) {
  const res = await fetch(`${API_BASE}/workflow/status/${workflowId}`);
  return res.json();
}
