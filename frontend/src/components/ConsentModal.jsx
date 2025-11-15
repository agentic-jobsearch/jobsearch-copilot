export default function ConsentModal({ job, onConfirm, onCancel }) {
  if (!job) return null;
  
  const jobTitle = job.title || job.job_title;
  const provider = job.provider || "Job Board";

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal">
        <h2>Confirm Auto-Apply</h2>
        <p className="modal-text">
          I am about to submit an application on your behalf for:
        </p>
        <p className="modal-job">
          {jobTitle} – {job.company}
        </p>
        <p className="modal-meta">
          Provider: {provider} • Location: {job.location}
        </p>
        <p className="modal-text small">
          By clicking “Confirm & Apply”, you consent to using your uploaded CV, transcript,
          and generated cover letter for this job only.
        </p>
        <div className="modal-actions">
          <button onClick={onCancel} className="modal-btn secondary">
            Cancel
          </button>
          <button onClick={onConfirm} className="modal-btn primary">
            Confirm & Apply
          </button>
        </div>
      </div>
    </div>
  );
}
