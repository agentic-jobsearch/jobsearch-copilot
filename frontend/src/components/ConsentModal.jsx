export default function ConsentModal({ job, onConfirm, onCancel }) {
  if (!job) return null;

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal">
        <h2>Confirm Auto-Apply</h2>
        <p className="modal-text">
          I am about to submit an application on your behalf for:
        </p>
        <p className="modal-job">
          {job.title} – {job.company}
        </p>
        <p className="modal-meta">
          Provider: {job.provider} • Location: {job.location}
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
