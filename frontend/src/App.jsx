import { useState, useRef, useEffect } from "react";
import ChatWindow from "./components/ChatWindow.jsx";
import JobList from "./components/JobList.jsx";
import ConsentModal from "./components/ConsentModal.jsx";
import "./App.css";

import {
  uploadDocs,
  startWorkflow,
  getWorkflowStatus,
  submitApplication
} from "./api/jobcopilot.js";

const generateMessageId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;

function App() {
  const [messages, setMessages] = useState(() => [
    {
      id: generateMessageId(),
      role: "assistant",
      content:
        "Hi, I’m your Job Agent. Upload your CV & transcript, tell me your career goal, and I’ll find and apply to aligned jobs for you."
    }
  ]);
  const [jobs, setJobs] = useState([]);
  const [generatedDocs, setGeneratedDocs] = useState(null);
  const [language, setLanguage] = useState("en");
  const [showConsent, setShowConsent] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [activePage, setActivePage] = useState("chats");
  const [profile, setProfile] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [visibleJobs, setVisibleJobs] = useState(5);
  const [removedJobIds, setRemovedJobIds] = useState(() => new Set());
  const [isUploading, setIsUploading] = useState(false);
  const [jobDocuments, setJobDocuments] = useState({});
  const [isPreparingApplication, setIsPreparingApplication] = useState(false);

  const cvInputRef = useRef(null);
  const transcriptInputRef = useRef(null);
  const typingTimers = useRef([]);
  const uploadedFilesRef = useRef([]);

  useEffect(() => {
    return () => {
      typingTimers.current.forEach((timer) => clearInterval(timer));
      typingTimers.current = [];
    };
  }, []);

  useEffect(() => {
    uploadedFilesRef.current = uploadedFiles;
  }, [uploadedFiles]);

  useEffect(() => {
    return () => {
      uploadedFilesRef.current.forEach((file) => URL.revokeObjectURL(file.url));
    };
  }, []);

  const createFileEntry = (file) => ({
    name: file.name,
    url: URL.createObjectURL(file),
    size: file.size
  });

  const addUploadedEntries = (files) => {
    if (!files.length) return;
    setUploadedFiles((prev) => {
      const updated = [...prev];
      const indexMap = new Map(prev.map((file, idx) => [file.name, { idx, url: file.url }]));

      files.forEach((file) => {
        const entry = createFileEntry(file);
        if (indexMap.has(entry.name)) {
          const { idx, url } = indexMap.get(entry.name);
          URL.revokeObjectURL(url);
          updated[idx] = entry;
        } else {
          updated.push(entry);
        }
      });

      return updated;
    });
  };

  const removeUploadedFile = (name) => {
    setUploadedFiles((prev) => {
      const remaining = [];
      prev.forEach((file) => {
        if (file.name === name) {
          URL.revokeObjectURL(file.url);
        } else {
          remaining.push(file);
        }
      });
      return remaining;
    });
  };

  const pushMessage = (message) => {
    const msg = { id: generateMessageId(), ...message };
    setMessages((prev) => [...prev, msg]);
    return msg;
  };

  const addAssistantMessageAnimated = (text) => {
    const safeText = text || "I processed your request.";
    const id = generateMessageId();
    const typingMessage = { id, role: "assistant", content: "", typing: true };
    setMessages((prev) => [...prev, typingMessage]);

    let index = 0;
    const interval = setInterval(() => {
      index += 1;
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === id
            ? { ...msg, content: safeText.slice(0, index) }
            : msg
        )
      );

      if (index >= safeText.length) {
        clearInterval(interval);
        typingTimers.current = typingTimers.current.filter((t) => t !== interval);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === id ? { ...msg, typing: false, content: safeText } : msg
          )
        );
      }
    }, 15);

    typingTimers.current.push(interval);
  };

  const buildClientId = (job, idx = 0) => {
    return (
      job._clientId ||
      job.job_id ||
      job.id ||
      job.jobId ||
      job.job_url ||
      job.url ||
      `${job.company || "company"}-${job.job_title || job.title || "role"}-${job.location || "anywhere"}-${idx}`
    );
  };

  const handleUpload = async () => {
    const cvFile = cvInputRef.current.files[0];
    const transcriptFile = transcriptInputRef.current.files[0];

    if (!cvFile && !transcriptFile) {
      alert("Please upload at least a CV or transcript.");
      return;
    }

    try {
      setIsUploading(true);
      const response = await uploadDocs(cvFile, transcriptFile);
      setProfile(response.profile || null);
      const newlySelected = [];
      if (cvFile) newlySelected.push(cvFile);
      if (transcriptFile) newlySelected.push(transcriptFile);
      addUploadedEntries(newlySelected);
      pushMessage({
        role: "assistant",
        content:
          "Documents uploaded! Now tell me your goal (e.g., 'Find data science jobs in Florida')."
      });
    } catch (err) {
      console.error(err);
      pushMessage({ role: "assistant", content: "Document upload failed." });
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveJob = (job) => {
    const jobId = job._clientId || buildClientId(job);
    setRemovedJobIds((prev) => {
      const next = new Set(prev);
      next.add(jobId);
      return next;
    });
    setJobs((prev) => prev.filter((j) => (j._clientId || buildClientId(j)) !== jobId));
  };


  const sendMessage = async (text) => {
  if (!text.trim()) return;
  pushMessage({ role: "user", content: text });
  setIsSending(true);

  try {
    // 1. Start workflow
    const start = await startWorkflow(text, language, profile);
    if (!start.workflow_id) throw new Error("No workflow_id received");

    // 2. Poll status until finished
    let done = false;
    let pollInterval = 1200;
    let result = null;
    let maxAttempts = 50; // 1 minute at 1200ms intervals
    let attempts = 0;

    while (!done && attempts < maxAttempts) {
      attempts++;
      const status = await getWorkflowStatus(start.workflow_id);

      if (status.status === "completed") {
        done = true;
        result = status;
      } else if (status.status === "failed") {
        throw new Error("Workflow failed");
      }

      if (!done) {
        await new Promise((res) => setTimeout(res, pollInterval));
      }
    }

    if (attempts >= maxAttempts) {
      throw new Error("Workflow timeout");
    }

    const analysisTask = result.tasks?.find(
      (t) => t.task_id === "goal_understanding" || t.task_type === "analysis"
    );
    const jobTask = result.tasks?.find((t) => t.task_type === "job_search");
    const rawJobMatches = jobTask?.output?.top_matches || [];
    const jobMatches = rawJobMatches.map((job, idx) => ({
      ...job,
      _clientId: buildClientId(job, idx)
    }));

    const replySections = [];

    const actions = analysisTask?.output?.actions;
    if (actions?.length) {
      const bullets = actions.map((action) => `• ${action}`).join("\n");
      replySections.push(`Suggested plan:\n${bullets}`);
    }

    const notes = analysisTask?.output?.notes;
    if (notes) {
      replySections.push(notes);
    }

    const insights = analysisTask?.output?.profile_insights;
    if (insights?.headline) {
      replySections.push(`Profile: ${insights.headline}`);
    }
    if (insights?.skills?.length) {
      replySections.push(`Key skills: ${insights.skills.join(", ")}`);
    }
    if (insights?.recent_role) {
      replySections.push(`Recent role: ${insights.recent_role}`);
    }

    const insightSummary = analysisTask?.output?.insight_summary;
    if (insightSummary?.skills?.length && !insights?.skills?.length) {
      replySections.push(`Key skills: ${insightSummary.skills.join(", ")}`);
    }
    if (insightSummary?.recent_role && !insights?.recent_role) {
      replySections.push(`Recent role: ${insightSummary.recent_role}`);
    }

    const jobSearchRan = jobTask?.output?.searched;

    if (jobMatches.length) {
      const sampleCount = Math.min(jobMatches.length, 5);
      const jobLines = jobMatches.slice(0, sampleCount).map((job) => {
        const company = job.company || job.company_name || job.company_urn || "Company";
        const location = job.location || "Location not provided";
        return `• ${job.job_title} @ ${company} (${location})`;
      });
      replySections.push(
        `Top matches (${jobMatches.length} found, showing ${sampleCount}):\n${jobLines.join("\n")}`
      );
      if (jobMatches.length > sampleCount) {
        replySections.push(`Open the Matched Jobs panel to view ${jobMatches.length - sampleCount} more.`);
      }
    } else if (jobSearchRan) {
      replySections.push("No strong matches yet. Try refining the goal or location.");
    }

    if (!replySections.length) {
      replySections.push("I'm processing your request.");
    }

    addAssistantMessageAnimated(replySections.join("\n\n"));
    const filteredJobs = jobMatches.filter((job) => !removedJobIds.has(job._clientId));

    setJobs(filteredJobs);
    setVisibleJobs(5);

  } catch (err) {
    console.error(err);
    pushMessage({ role: "assistant", content: "Something went wrong." });
  } finally {
    setIsSending(false);
  }
};

  const handleApplyClick = (job) => {
    setSelectedJob(job);
    setShowConsent(true);
  };

const stripMarkdownFence = (text) => {
  if (!text) return "";
  let cleaned = text.trim();
  if (cleaned.startsWith("```")) {
    const firstNewLine = cleaned.indexOf("\n");
    if (firstNewLine !== -1) {
      cleaned = cleaned.slice(firstNewLine + 1);
    }
    if (cleaned.endsWith("```")) {
      cleaned = cleaned.slice(0, -3);
    }
  }
  return cleaned.trim();
};

const confirmApply = async () => {
  if (!selectedJob) return;
  setShowConsent(false);
  setIsPreparingApplication(true);

  try {
    const response = await submitApplication(selectedJob);

    setGeneratedDocs({
      cv: stripMarkdownFence(response.resume) || "Resume generated.",
      coverLetter: stripMarkdownFence(response.cover_letter) || "Cover letter generated.",
      cvPdf: response.resume_pdf || null,
      coverPdf: response.cover_letter_pdf || null
    });

    const jobKey = selectedJob._clientId || buildClientId(selectedJob);
    setJobDocuments((prev) => ({
      ...prev,
      [jobKey]: {
        resumePdf: response.resume_pdf || null,
        coverPdf: response.cover_letter_pdf || null
      }
    }));

    pushMessage({
      role: "assistant",
      content: `Tailored resume and cover letter prepared for "${selectedJob.title}" at ${selectedJob.company}.`
    });
  } catch (err) {
    console.error(err);
    pushMessage({ role: "assistant", content: err.message || "Application workflow failed." });
  } finally {
    setSelectedJob(null);
    setIsPreparingApplication(false);
  }
};

  return (
    <div className="app-root">
      {/* LEFT SIDEBAR */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-circle" />
          <span className="logo-text">CareerCortex</span>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activePage === "chats" ? "nav-item-active" : ""}`}
            onClick={() => setActivePage("chats")}
          >
            <span className={`nav-pill ${activePage === "chats" ? "" : "muted"}`} />
            <span>Chats</span>
          </button>

          <button
            className={`nav-item ${activePage === "jobboard" ? "nav-item-active" : ""}`}
            onClick={() => setActivePage("jobboard")}
          >
            <span className={`nav-pill ${activePage === "jobboard" ? "" : "muted"}`} />
            <span>Job Board</span>
          </button>
        </nav>


        <div className="sidebar-bottom">
          <button className="sidebar-link">⚙ Settings</button>
          <button className="sidebar-link">↩ Log out</button>

          <div className="user-card">
            <div className="user-avatar">J</div>
            <div className="user-info">
              <div className="user-name">Jannat</div>
              <div className="user-email">you@example.com</div>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN PANEL */}
      <main className="main-panel">
        <header className="main-header">
        <div>
          {activePage === "chats" ? (
            <>
              <h1>Hi, I’m your Job Agent</h1>
              <p>Tell me your goal, and get complete job search & application plans.</p>
            </>
          ) : (
            <>
              <h1>Explore Personalized Job Matches</h1>
              <p>Preview features, discover aligned roles, and plan your next move.</p>
            </>
          )}
        </div>

        {activePage === "chats" && (
          <div className="upload-wrapper">
            <div className="upload-label">Upload CV & Transcript</div>
            <div className="upload-inputs">
              <input
                type="file"
                accept=".pdf,.txt,.doc,.docx"
                ref={cvInputRef}
                aria-label="Upload CV"
              />
              <input
                type="file"
                accept=".pdf,.txt,.doc,.docx"
                ref={transcriptInputRef}
                aria-label="Upload academic transcript"
              />
              <button
                type="button"
                onClick={handleUpload}
                disabled={isUploading}
                className={`upload-btn ${isUploading ? "uploading" : ""}`}
              >
                {isUploading ? (
                  <>
                    <span className="upload-spinner" />
                    Uploading...
                  </>
                ) : (
                  "Upload"
                )}
              </button>
            </div>
            <div className="language-select">
              <label>Language:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                aria-label="Select language"
              >
                <option value="en">English</option>
                <option value="es">Español</option>
              </select>
            </div>
          </div>
        )}
        </header>

        {activePage === "jobboard" && (
          <section className="feature-section">
            <h2>Here is what you got!</h2>
            <div className="feature-grid">
              <FeatureCard title="Guided Job Search" percent="100%" color="#ff8b3d" />
              <FeatureCard title="Aligned Job Links" percent="92%" color="#ffe45e" />
              <FeatureCard title="Save & Track Jobs" percent="76%" color="#48c6ef" />
              <FeatureCard title="Chat with AI" percent="100%" color="#ff6ad5" />
              <FeatureCard title="Tailored CVs" percent="88%" color="#7cfc9e" />
              <FeatureCard title="Cover Letters & PDFs" percent="81%" color="#a694ff" />
            </div>
          </section>
        )}


        {activePage === "chats" && (
          <section className="content-row">
            <div className="content-left">
              <ChatWindow
                messages={messages}
                onSendMessage={sendMessage}
                disabled={isSending}
                language={language}
                isProcessing={isSending}
              />
            </div>
            <div className="content-right">
              <JobList
                jobs={jobs}
                generatedDocs={generatedDocs}
                uploadedFiles={uploadedFiles}
                profile={profile}
                visibleJobs={visibleJobs}
                onLoadMore={() => setVisibleJobs((prev) => prev + 5)}
                onRemoveFile={removeUploadedFile}
                jobDocuments={jobDocuments}
                onRemoveJob={handleRemoveJob}
                onApplyClick={handleApplyClick}
              />
            </div>
          </section>
        )}

      </main>

      {showConsent && (
        <ConsentModal
          job={selectedJob}
          onConfirm={confirmApply}
          onCancel={() => setShowConsent(false)}
        />
      )}
      {isPreparingApplication && <PreparingModal />}
    </div>
  );
}

function FeatureCard({ title, percent, color }) {
  return (
    <div className="feature-card">
      <div className="feature-title">{title}</div>
      <div className="feature-footer">
        <span className="feature-percent">{percent}</span>
        <div className="feature-bar">
          <span className="feature-bar-fill" style={{ backgroundColor: color }} />
        </div>
      </div>
    </div>
  );
}

export default App;

function PreparingModal() {
  return (
    <div className="modal-backdrop preparing">
      <div className="preparing-modal">
        <div className="preparing-spinner">
          <span />
          <span />
          <span />
        </div>
        <p>Preparing your application…</p>
      </div>
    </div>
  );
}
