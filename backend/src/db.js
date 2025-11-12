import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create/open database in the data directory
const dbPath = path.join(__dirname, "../../data/userProfiles.db");
const db = new Database(dbPath);

// Enable WAL mode for better concurrent access
db.pragma("journal_mode = WAL");

// Create user_profiles table if it doesn't exist
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
const getProfileStmt = db.prepare(
  "SELECT * FROM user_profiles WHERE user_id = ?"
);

const upsertProfileStmt = db.prepare(`
  INSERT INTO user_profiles (user_id, cv_text, transcript_text, structured_profile, updated_at)
  VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
  ON CONFLICT(user_id) DO UPDATE SET
    cv_text = COALESCE(excluded.cv_text, cv_text),
    transcript_text = COALESCE(excluded.transcript_text, transcript_text),
    structured_profile = COALESCE(excluded.structured_profile, structured_profile),
    updated_at = CURRENT_TIMESTAMP
`);

/**
 * Get a user profile from the database
 * @param {string} userId - The user ID
 * @returns {Object|null} The user profile or null if not found
 */
export function getUserProfile(userId) {
  const row = getProfileStmt.get(userId);
  if (!row) return null;

  return {
    cvText: row.cv_text || "",
    transcriptText: row.transcript_text || "",
    structuredProfile: row.structured_profile
      ? JSON.parse(row.structured_profile)
      : null,
  };
}

/**
 * Save or update a user profile in the database
 * @param {string} userId - The user ID
 * @param {Object} profile - The profile data
 * @param {string} [profile.cvText] - CV text
 * @param {string} [profile.transcriptText] - Transcript text
 * @param {Object} [profile.structuredProfile] - Structured profile data
 */
export function saveUserProfile(userId, profile) {
  const structuredProfileJson = profile.structuredProfile
    ? JSON.stringify(profile.structuredProfile)
    : null;

  upsertProfileStmt.run(
    userId,
    profile.cvText || null,
    profile.transcriptText || null,
    structuredProfileJson
  );
}

/**
 * Close the database connection
 */
export function closeDatabase() {
  db.close();
}

export default { getUserProfile, saveUserProfile, closeDatabase };
