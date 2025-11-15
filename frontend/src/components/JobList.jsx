import { useState } from "react";

export default function JobList({
  jobs,
  generatedDocs,
  uploadedFiles = [],
  profile,
  visibleJobs = 5,
  onLoadMore,
  onRemoveFile = () => {},
  onRemoveJob = () => {},
  jobDocuments = {},
  preparedJobs = new Set(),
  onPrepareJob = () => {},
  onApplyClick,
  appliedJobs = []
}) {
  const [modalJob, setModalJob] = useState(null);
  const skills = Array.isArray(profile?.skills) ? profile.skills.slice(0, 8) : [];
  const summaryLines = [];
  if (profile?.title) summaryLines.push(profile.title);
  if (profile?.location) summaryLines.push(`Based in ${profile.location}`);
  if (profile?.years_experience) {
    summaryLines.push(`${profile.years_experience}+ years of experience`);
  }

  return (
    <div className="jobs-card">
      {uploadedFiles.length > 0 && (
        <div className="uploaded-files-card">
          <div className="uploaded-files-header">
            <h4>Uploaded Documents</h4>
            <span>{uploadedFiles.length}</span>
          </div>
          <ul>
            {uploadedFiles.map((file) => (
              <li key={file.name} className="uploaded-file-item">
                <a
                  href={file.url}
                  download={file.name}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {file.name}
                </a>
                <button
                  type="button"
                  className="uploaded-file-remove"
                  onClick={() => onRemoveFile(file.name)}
                  aria-label={`Remove ${file.name}`}
                >
                  🗑
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      {profile && (
        <div className="profile-summary-card">
          <div className="profile-summary-header">
            <h4>Resume Insights</h4>
            {profile.name && <span>{profile.name}</span>}
          </div>
          <div className="profile-summary-body">
            {summaryLines.length > 0 && (
              <p>{summaryLines.join(" • ")}</p>
            )}
            {skills.length > 0 ? (
              <div className="profile-skills">
                {skills.map((skill) => (
                  <span key={skill}>{skill}</span>
                ))}
              </div>
            ) : (
              <p className="profile-summary-placeholder">
                We parsed your résumé but didn’t detect explicit skills.
              </p>
            )}
          </div>
        </div>
      )}
      <h3 className="jobs-title">Matched Jobs</h3>
      <p className="jobs-subtitle">
        Based on your CV & transcript. Review and apply with one click.
      </p>

      <div className="jobs-list">
        {jobs.length === 0 && (
          <p className="jobs-empty">
            No jobs yet. Try: “Find junior software engineering jobs in Florida”.
          </p>
        )}

        {jobs.slice(0, visibleJobs).map((job) => {
          const matchScore = job.matchScore ?? job.match_score ?? 0;
          const jobId = job._clientId || job.id || job.job_id;
          const docs = jobDocuments[jobId];
          const isPrepared = preparedJobs.has(jobId);

          return (
            <div key={jobId} className="job-item">
      <div className="job-main">
        <div>
          <div className="job-title-row">
            <span className="job-company">{job.company}</span>
            <button
              type="button"
              className="job-title-link"
              onClick={() => setModalJob(job)}
            >
              {job.job_title || job.title || "View role"}
            </button>
          </div>
          <div className="job-meta">
            {job.location} • Match score: <strong>{matchScore}</strong>
          </div>
          {job.matched_skills?.length > 0 && (
            <div className="job-skills">
              {job.matched_skills.slice(0, 8).map((skill) => (
                <span key={`${jobId}-${skill}`}>{skill}</span>
              ))}
            </div>
          )}
        </div>
        <div className="job-actions">
          <button
            className="job-remove-btn"
            onClick={() => onRemoveJob(job)}
            aria-label={`Remove ${job.title}`}
          >
            Remove
          </button>

          {!isPrepared && (
            <button
              className="job-prepare-btn"
              onClick={() => onPrepareJob(job)}
              aria-label={`Prepare documents for ${job.title}`}
            >
              Prepare
            </button>
          )}

          {isPrepared && (docs?.resumePdf || docs?.coverPdf) && (
            <>
              {docs.resumePdf && (
                <button
                  type="button"
                  className="job-download-btn"
                  onClick={() => downloadBase64Pdf(docs.resumePdf, `${job.company || "resume"}.pdf`)}
                >
                  Resume
                </button>
              )}
              {docs.coverPdf && (
                <button
                  type="button"
                  className="job-download-btn"
                  onClick={() => downloadBase64Pdf(docs.coverPdf, `${job.company || "cover_letter"}.pdf`)}
                >
                  Cover Letter
                </button>
              )}
              <button
                className="job-apply-btn"
                onClick={() => onApplyClick(job)}
                aria-label={`Apply to ${job.title} at ${job.company}`}
              >
                Apply
              </button>
            </>
          )}
        </div>
        </div>
        {(!docs || (!docs.resumePdf && !docs.coverPdf)) && job.url && (
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="job-link"
          >
            View posting
          </a>
        )}
            </div>
          );
        })}
      </div>
      {jobs.length > visibleJobs && (
        <button className="jobs-load-more" onClick={onLoadMore}>
          Show more ({jobs.length - visibleJobs} remaining)
        </button>
      )}

      {appliedJobs.length > 0 && (
        <div className="applied-section">
          <h3 className="jobs-title">Positions Applied To</h3>
          <div className="jobs-list">
            {appliedJobs.map((job) => {
              const jobId = job._clientId || job.id || job.job_id;
              const docs = job.documents || {};
              return (
                <div key={jobId} className="job-item">
                  <div className="job-main">
                    <div>
                      <div className="job-title">{job.title}</div>
                      <div className="job-company">{job.company}</div>
                      <div className="job-meta">{job.location}</div>
                    </div>
                    <div className="job-actions">
                      {docs.resumePdf && (
                        <button
                          type="button"
                          className="job-download-btn"
                          onClick={() => downloadBase64Pdf(docs.resumePdf, `${job.company || "resume"}.pdf`)}
                        >
                          Resume
                        </button>
                      )}
                      {docs.coverPdf && (
                        <button
                          type="button"
                          className="job-download-btn"
                          onClick={() => downloadBase64Pdf(docs.coverPdf, `${job.company || "cover_letter"}.pdf`)}
                        >
                          Cover Letter
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {modalJob && (
        <div className="modal-backdrop">
          <div className="job-description-modal">
            <h3>{modalJob.title}</h3>
            <p className="modal-job">{modalJob.company}</p>
            <p className="modal-meta">{modalJob.location}</p>
            <div className="job-description-body">
              {modalJob.description || "No job description provided."}
            </div>
            <button className="modal-btn primary" onClick={() => setModalJob(null)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function downloadBase64Pdf(base64Data, filename) {
  if (!base64Data) return;
  const byteCharacters = atob(base64Data);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const blob = new Blob([new Uint8Array(byteNumbers)], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
