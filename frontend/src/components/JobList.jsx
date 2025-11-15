export default function JobList({
  jobs,
  generatedDocs,
  uploadedFiles = [],
  profile,
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
              <li key={file}>{file}</li>
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

        {jobs.map((job) => {
          const matchScore = job.matchScore ?? job.match_score ?? 0;
          const jobId = job.id || job.job_id;
          const jobTitle = job.title || job.job_title;
          const jobUrl = job.url || job.job_url;

          return (
            <div key={jobId} className="job-item">
              <div className="job-main">
                <div>
                  <div className="job-title">{jobTitle}</div>
                  <div className="job-company">{job.company}</div>
                  <div className="job-meta">
                    {job.location} • Match score: {matchScore}
                  </div>
                </div>
                <button
                  className="job-apply-btn"
                  onClick={() => onApplyClick(job)}
                  aria-label={`Apply to ${jobTitle} at ${job.company}`}
                >
                  Apply
                </button>
              </div>
              {jobUrl && (
                <a
                  href={jobUrl}
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
