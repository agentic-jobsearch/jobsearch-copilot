import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create data directory if it doesn't exist
const dataDir = path.join(__dirname, "..", "data");
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

const dbPath = path.join(dataDir, "userprofiles.db");
const db = new Database(dbPath);

// Initialize database schema
db.exec(`
  CREATE TABLE IF NOT EXISTS user_profiles (
    user_id TEXT PRIMARY KEY,
    cv_text TEXT,
    transcript_text TEXT,
    structured_profile TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

// Prepared statements for better performance
const statements = {
  getProfile: db.prepare("SELECT * FROM user_profiles WHERE user_id = ?"),
  
  upsertProfile: db.prepare(`
    INSERT INTO user_profiles (user_id, cv_text, transcript_text, structured_profile, updated_at)
    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(user_id) DO UPDATE SET
      cv_text = excluded.cv_text,
      transcript_text = excluded.transcript_text,
      structured_profile = excluded.structured_profile,
      updated_at = CURRENT_TIMESTAMP
  `),
  
  updateStructuredProfile: db.prepare(`
    UPDATE user_profiles 
    SET structured_profile = ?, updated_at = CURRENT_TIMESTAMP
    WHERE user_id = ?
  `),
};

export const userProfileDb = {
  /**
   * Get user profile by userId
   * @param {string} userId 
   * @returns {object|null} User profile or null if not found
   */
  getProfile(userId) {
    const row = statements.getProfile.get(userId);
    if (!row) return null;
    
    return {
      cvText: row.cv_text || "",
      transcriptText: row.transcript_text || "",
      structuredProfile: row.structured_profile ? JSON.parse(row.structured_profile) : null,
    };
  },

  /**
   * Save or update user profile
   * @param {string} userId 
   * @param {object} profile - { cvText, transcriptText, structuredProfile }
   */
  saveProfile(userId, profile) {
    const structuredProfileJson = profile.structuredProfile 
      ? JSON.stringify(profile.structuredProfile) 
      : null;
    
    statements.upsertProfile.run(
      userId,
      profile.cvText || "",
      profile.transcriptText || "",
      structuredProfileJson
    );
  },

  /**
   * Update only the structured profile for a user
   * @param {string} userId 
   * @param {object} structuredProfile 
   */
  updateStructuredProfile(userId, structuredProfile) {
    const structuredProfileJson = structuredProfile 
      ? JSON.stringify(structuredProfile) 
      : null;
    
    statements.updateStructuredProfile.run(structuredProfileJson, userId);
  },

  /**
   * Close database connection (call on server shutdown)
   */
  close() {
    db.close();
  },
};
