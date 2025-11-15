export default function JobList({
  jobs,
  generatedDocs,
  uploadedFiles = [],
  profile,
  visibleJobs = 5,
  onLoadMore,
  onRemoveFile = () => {},
  onRemoveJob = () => {},
  onApplyClick
}) {
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
          const jobId = job.id || job.job_id;

          return (
            <div key={jobId} className="job-item">
      <div className="job-main">
        <div>
          <div className="job-title">{job.title}</div>
          <div className="job-company">{job.company}</div>
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
                  <button
                    className="job-apply-btn"
                    onClick={() => onApplyClick(job)}
                    aria-label={`Apply to ${job.title} at ${job.company}`}
                  >
                    Apply
                  </button>
                </div>
              </div>
              {job.url && (
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

      {generatedDocs && (
        <div className="docs-preview">
          <h4>Generated CV (preview)</h4>
          <pre>{generatedDocs.cv}</pre>
          <h4>Cover Letter (preview)</h4>
          <pre>{generatedDocs.coverLetter}</pre>
        </div>
      )}
    </div>
  );
}
