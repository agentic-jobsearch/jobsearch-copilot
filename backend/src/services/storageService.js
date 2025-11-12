import Redis from "ioredis";

class StorageService {
  constructor() {
    this.redis = null;
    this.fallbackStore = new Map(); // Fallback to in-memory if Redis unavailable
    this.isRedisAvailable = false;
  }

  async initialize() {
    try {
      const redisUrl = process.env.REDIS_URL || "redis://localhost:6379";
      this.redis = new Redis(redisUrl, {
        maxRetriesPerRequest: 3,
        enableReadyCheck: true,
        lazyConnect: true,
      });

      // Test connection
      await this.redis.connect();
      await this.redis.ping();
      this.isRedisAvailable = true;
      console.log("✓ Redis connection established");
    } catch (error) {
      console.warn("⚠ Redis unavailable, using in-memory fallback:", error.message);
      this.isRedisAvailable = false;
      if (this.redis) {
        this.redis.disconnect();
        this.redis = null;
      }
    }
  }

  async setProfile(userId, profile) {
    try {
      if (this.isRedisAvailable && this.redis) {
        const key = `user:profile:${userId}`;
        await this.redis.set(key, JSON.stringify(profile));
      } else {
        this.fallbackStore.set(userId, profile);
      }
    } catch (error) {
      console.error("Error storing profile:", error);
      // Fallback to in-memory on Redis failure
      this.fallbackStore.set(userId, profile);
    }
  }

  async getProfile(userId) {
    try {
      if (this.isRedisAvailable && this.redis) {
        const key = `user:profile:${userId}`;
        const data = await this.redis.get(key);
        return data ? JSON.parse(data) : null;
      } else {
        return this.fallbackStore.get(userId) || null;
      }
    } catch (error) {
      console.error("Error retrieving profile:", error);
      // Fallback to in-memory on Redis failure
      return this.fallbackStore.get(userId) || null;
    }
  }

  async deleteProfile(userId) {
    try {
      if (this.isRedisAvailable && this.redis) {
        const key = `user:profile:${userId}`;
        await this.redis.del(key);
      } else {
        this.fallbackStore.delete(userId);
      }
    } catch (error) {
      console.error("Error deleting profile:", error);
      this.fallbackStore.delete(userId);
    }
  }

  async close() {
    if (this.redis) {
      await this.redis.quit();
    }
  }
}

// Export singleton instance
const storageService = new StorageService();
export default storageService;
