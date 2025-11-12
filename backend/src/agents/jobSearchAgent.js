export async function findMatchingJobs(structuredProfile, userMessage = "") {
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
  const messageLower = userMessage.toLowerCase();

  return baseJobs
    .map((job) => {
      const overlap = job.requiredSkills.filter((s) => skills.includes(s)).length;
      let matchScore = overlap;
      
      // Boost score if job title or company matches keywords in user message
      if (messageLower && (
        messageLower.includes(job.title.toLowerCase()) ||
        messageLower.includes(job.company.toLowerCase()) ||
        job.requiredSkills.some(skill => messageLower.includes(skill.toLowerCase()))
      )) {
        matchScore += 0.5;
      }
      
      return { ...job, matchScore };
    })
    .filter((job) => job.matchScore > 0)
    .sort((a, b) => b.matchScore - a.matchScore);
}
