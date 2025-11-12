import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Storage directory for user profiles
const STORAGE_DIR = path.join(__dirname, "../../data/user-profiles");

/**
 * Simple file-based persistent storage for user profiles
 * Each user profile is stored as a separate JSON file
 */
class UserProfileStorage {
  constructor() {
    this.ensureStorageDir();
  }

  /**
   * Ensure the storage directory exists
   */
  async ensureStorageDir() {
    try {
      await fs.mkdir(STORAGE_DIR, { recursive: true });
    } catch (error) {
      console.error("Error creating storage directory:", error);
    }
  }

  /**
   * Get the file path for a user's profile
   */
  getUserFilePath(userId) {
    // Sanitize userId to prevent directory traversal
    const sanitized = userId.replace(/[^a-zA-Z0-9-_]/g, "_");
    return path.join(STORAGE_DIR, `${sanitized}.json`);
  }

  /**
   * Get a user profile
   * @param {string} userId - The user ID
   * @returns {Promise<Object|null>} The user profile or null if not found
   */
  async get(userId) {
    try {
      const filePath = this.getUserFilePath(userId);
      const data = await fs.readFile(filePath, "utf8");
      return JSON.parse(data);
    } catch (error) {
      if (error.code === "ENOENT") {
        return null; // File doesn't exist
      }
      console.error(`Error reading profile for user ${userId}:`, error);
      return null;
    }
  }

  /**
   * Set/update a user profile
   * @param {string} userId - The user ID
   * @param {Object} profile - The user profile data
   */
  async set(userId, profile) {
    try {
      await this.ensureStorageDir();
      const filePath = this.getUserFilePath(userId);
      await fs.writeFile(filePath, JSON.stringify(profile, null, 2), "utf8");
    } catch (error) {
      console.error(`Error writing profile for user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Delete a user profile
   * @param {string} userId - The user ID
   */
  async delete(userId) {
    try {
      const filePath = this.getUserFilePath(userId);
      await fs.unlink(filePath);
    } catch (error) {
      if (error.code !== "ENOENT") {
        console.error(`Error deleting profile for user ${userId}:`, error);
      }
    }
  }

  /**
   * Check if a user profile exists
   * @param {string} userId - The user ID
   * @returns {Promise<boolean>}
   */
  async has(userId) {
    try {
      const filePath = this.getUserFilePath(userId);
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }
}

export default new UserProfileStorage();
