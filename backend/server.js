import express from "express";
import cors from "cors";
import multer from "multer";
import { PDFParse } from "pdf-parse";
import dotenv from "dotenv";
import { runJobChatFlow } from "./src/agents/orchestrator.js";
import storageService from "./src/services/storageService.js";

dotenv.config();

const app = express();
const port = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

const upload = multer({ storage: multer.memoryStorage() });

app.post(
  "/api/upload-docs",
  upload.fields([{ name: "cv" }, { name: "transcript" }]),
  async (req, res) => {
    try {
      const { userId = "demo-user" } = req.body;

      const cvFile = req.files["cv"]?.[0];
      const transcriptFile = req.files["transcript"]?.[0];

      const parseFile = async (file) => {
        if (!file) return "";
        if (file.mimetype === "application/pdf") {
          const data = await PDFParse(file.buffer);
          return data.text;
        }
        return file.buffer.toString("utf8");
      };

      const cvText = await parseFile(cvFile);
      const transcriptText = await parseFile(transcriptFile);

      await storageService.setProfile(userId, {
        cvText,
        transcriptText,
        structuredProfile: null
      });

      res.json({ success: true, message: "Documents uploaded." });
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: "Failed to process documents." });
    }
  }
);

app.post("/api/chat", async (req, res) => {
  try {
    const { message, language = "en", userId = "demo-user" } = req.body;

    const profile = await storageService.getProfile(userId) || {
      cvText: "",
      transcriptText: "",
      structuredProfile: null
    };

    const result = await runJobChatFlow({
      userMessage: message,
      language,
      profile,
      userId
    });

    if (result.updatedProfile) {
      await storageService.setProfile(userId, {
        ...profile,
        structuredProfile: result.updatedProfile
      });
    }

    res.json({
      reply: result.reply,
      jobs: result.jobs,
      generatedDocs: result.generatedDocs
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Chat processing failed." });
  }
});

app.post("/api/apply", async (req, res) => {
  try {
    const { jobId, provider, userId = "demo-user", allowAutoApply } = req.body;

    if (!allowAutoApply) {
      return res.status(400).json({
        error: "User consent is required for auto-apply."
      });
    }

    console.log(`Simulating application for ${userId} to job ${jobId} @ ${provider}`);

    res.json({
      success: true,
      message: "Application submitted (simulated for demo)."
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to apply to job." });
  }
});

// Initialize storage service before starting server
await storageService.initialize();

const server = app.listen(port, () => {
  console.log(`Job Agent backend listening on http://localhost:${port}`);
});

// Graceful shutdown
process.on("SIGTERM", async () => {
  console.log("SIGTERM received, closing server gracefully...");
  server.close(async () => {
    await storageService.close();
    process.exit(0);
  });
});

process.on("SIGINT", async () => {
  console.log("SIGINT received, closing server gracefully...");
  server.close(async () => {
    await storageService.close();
    process.exit(0);
  });
});
