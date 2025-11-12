import { useState, useRef } from "react";
import ChatWindow from "./components/ChatWindow.jsx";
import JobList from "./components/JobList.jsx";
import ConsentModal from "./components/ConsentModal.jsx";
import "./App.css";

const API_BASE = "http://localhost:4000";

function App() {
  const [messages, setMessages] = useState([
    {
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

  const cvInputRef = useRef(null);
  const transcriptInputRef = useRef(null);

  const handleUpload = async () => {
    const cvFile = cvInputRef.current.files[0];
    const transcriptFile = transcriptInputRef.current.files[0];

    if (!cvFile && !transcriptFile) {
      alert("Please upload at least a CV or transcript.");
      return;
    }

    const formData = new FormData();
    if (cvFile) formData.append("cv", cvFile);
    if (transcriptFile) formData.append("transcript", transcriptFile);
    formData.append("userId", "demo-user");

    await fetch(`${API_BASE}/api/upload-docs`, {
      method: "POST",
      body: formData
    });

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content:
          "Thanks! Now type or say what kind of roles you are targeting (e.g., “junior data scientist in Florida”)."
      }
    ]);
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsSending(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          language,
          userId: "demo-user"
        })
      });

      const data = await res.json();
      if (data.error) throw new Error(data.error);

      const assistantMsg = { role: "assistant", content: data.reply };
      setMessages((prev) => [...prev, assistantMsg]);
      setJobs(data.jobs || []);
      setGeneratedDocs(data.generatedDocs || null);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong talking to the backend." }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleApplyClick = (job) => {
    setSelectedJob(job);
    setShowConsent(true);
  };

  const confirmApply = async () => {
    if (!selectedJob) return;
    try {
      const res = await fetch(`${API_BASE}/api/apply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jobId: selectedJob.id,
          provider: selectedJob.provider,
          userId: "demo-user",
          allowAutoApply: true
        })
      });

      const data = await res.json();
      if (data.error) throw new Error(data.error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `I submitted your application for "${selectedJob.title}" at ${selectedJob.company} (simulated).`
        }
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Failed to apply for the job." }
      ]);
    } finally {
      setShowConsent(false);
      setSelectedJob(null);
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
              <button onClick={handleUpload}>Upload</button>
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
              />
            </div>
            <div className="content-right">
              <JobList
                jobs={jobs}
                generatedDocs={generatedDocs}
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
