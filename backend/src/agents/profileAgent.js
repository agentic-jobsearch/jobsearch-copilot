export async function buildStructuredProfile(cvText, transcriptText) {
  const text = `${cvText}\n${transcriptText}`.toLowerCase();

  const skills = [];
  const skillKeywords = [
    "python",
    "java",
    "javascript",
    "react",
    "node",
    "machine learning",
    "data science",
    "sql",
    "golang"
  ];

  for (const s of skillKeywords) {
    if (text.includes(s)) skills.push(s);
  }

  const degree = text.includes("master")
    ? "Master's"
    : text.includes("bachelor")
    ? "Bachelor's"
    : "Unknown";

  return {
    name: "Unknown",
    degree,
    skills: [...new Set(skills)],
    rawText: text
  };
}
