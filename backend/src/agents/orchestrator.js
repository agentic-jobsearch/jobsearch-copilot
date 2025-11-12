import { buildStructuredProfile } from "./profileAgent.js";
import { findMatchingJobs } from "./jobSearchAgent.js";
import { generateApplicationDocs } from "./applicationAgent.js";

export async function runJobChatFlow({ userMessage, language, profile }) {
  const structuredProfile =
    profile.structuredProfile ||
    (await buildStructuredProfile(profile.cvText, profile.transcriptText, language));

  const lower = userMessage.toLowerCase();
  let mode = "general";

  if (lower.includes("find") && lower.includes("job")) mode = "job_search";
  if (lower.includes("apply") || lower.includes("cover letter")) mode = "apply";

  let reply = "";
  let jobs = [];
  let generatedDocs = null;

  if (mode === "job_search") {
    jobs = await findMatchingJobs(structuredProfile);
    reply =
      jobs.length > 0
        ? `I found ${jobs.length} jobs that match your profile. You can review them below and click "Apply" after giving consent.`
        : "I couldn't find strong matches yet. Try refining your target role or location.";
  } else if (mode === "apply") {
    reply =
      "Select a job from the list and click Apply. I will generate a tailored CV and cover letter and apply only after you confirm.";
  } else {
    reply =
      "I'm your Job Finder Agent. You can ask me to find data science, software engineering, or other roles based on your CV and transcript, and I can help generate tailored CVs and cover letters.";
  }

  if (jobs.length > 0) {
    generatedDocs = await generateApplicationDocs(structuredProfile, jobs[0]);
  }

  return {
    reply,
    jobs,
    generatedDocs,
    updatedProfile: structuredProfile
  };
}
