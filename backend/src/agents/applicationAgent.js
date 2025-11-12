export async function generateApplicationDocs(structuredProfile, job) {
  const { degree, skills } = structuredProfile;

  const cv = `
Tailored CV for ${job.title} at ${job.company}

Degree: ${degree}
Key Skills: ${skills.join(", ")}

Experience:
- Describe your most relevant experience here for ${job.title}.
`;

  const coverLetter = `
Dear Hiring Manager,

I am excited to apply for the ${job.title} position at ${job.company}. With my background in ${degree} and hands-on experience using ${skills.join(
    ", "
  )}, I believe I am a strong fit for this role.

In previous projects, I have demonstrated my ability to learn quickly, collaborate with teams, and deliver impactful results. I am particularly interested in this opportunity because it aligns with my interests and long-term career goals.

Thank you for considering my application.

Sincerely,
[Your Name]
`;

  return { cv, coverLetter };
}
