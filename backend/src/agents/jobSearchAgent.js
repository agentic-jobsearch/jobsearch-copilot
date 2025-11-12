export async function findMatchingJobs(structuredProfile) {
  const baseJobs = [
    {
      id: "job-1",
      title: "Junior Data Scientist",
      company: "Insight Analytics",
      location: "Remote",
      provider: "MockLinkedIn",
      url: "https://example.com/jobs/1",
      requiredSkills: ["python", "machine learning"]
    },
    {
      id: "job-2",
      title: "Full Stack Developer (React/Node)",
      company: "TechWave",
      location: "Hybrid - Miami, FL",
      provider: "MockIndeed",
      url: "https://example.com/jobs/2",
      requiredSkills: ["javascript", "react", "node"]
    },
    {
      id: "job-3",
      title: "Backend Engineer (Golang)",
      company: "CloudCore",
      location: "Remote",
      provider: "MockAdzuna",
      url: "https://example.com/jobs/3",
      requiredSkills: ["golang", "sql"]
    }
  ];

  const skills = structuredProfile.skills || [];

  return baseJobs
    .map((job) => {
      const overlap = job.requiredSkills.filter((s) => skills.includes(s)).length;
      return { ...job, matchScore: overlap };
    })
    .filter((job) => job.matchScore > 0)
    .sort((a, b) => b.matchScore - a.matchScore);
}
