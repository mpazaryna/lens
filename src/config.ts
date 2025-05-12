/**
 * Configuration management for the Lens application.
 *
 * This module handles loading configuration from .env files and environment variables,
 * providing a typed configuration object with validation.
 */

import { load } from "@std/dotenv";
import { join } from "@std/path";
import { Result, Ok, Err } from "@monads";

/**
 * Core application configuration
 */
export interface CoreConfig {
  dataDir: string;
  logLevel: "debug" | "info" | "warn" | "error";
  port: number;
}

/**
 * LLM configuration
 */
export interface LLMConfig {
  ollamaBaseUrl: string;
  embeddingModel: string;
  llmModel: string;
}

/**
 * LangChain configuration
 */
export interface LangChainConfig {
  tracing: boolean;
}

/**
 * LangSmith configuration
 */
export interface LangSmithConfig {
  apiKey: string;
  project: string;
  tracingEnabled: boolean;
}

/**
 * Database configuration
 */
export interface DatabaseConfig {
  dbPath: string;
  vectorDbUrl?: string;
}

/**
 * Complete application configuration
 */
export interface AppConfig {
  core: CoreConfig;
  llm: LLMConfig;
  langChain: LangChainConfig;
  langSmith: LangSmithConfig;
  database: DatabaseConfig;
}

/**
 * Configuration error
 */
export class ConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ConfigError";
  }
}

/**
 * Get the default data directory based on the operating system
 */
export function defaultDataDir(): string {
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE") || ".";

  if (Deno.build.os === "darwin") {
    return join(homeDir, "Library", "Application Support", "lens");
  } else if (Deno.build.os === "windows") {
    return join(homeDir, "AppData", "Roaming", "lens");
  } else {
    return join(homeDir, ".config", "lens");
  }
}

/**
 * Load configuration from .env file and environment variables
 */
export async function loadConfig(): Promise<Result<AppConfig, ConfigError>> {
  try {
    // Try to load .env file (no error if it doesn't exist)
    let dotEnvConfig: Record<string, string> = {};
    try {
      dotEnvConfig = await load();
    } catch (error) {
      // .env file doesn't exist or couldn't be read - that's fine
      console.log("No .env file found, using environment variables and defaults only");
    }

    // Helper function to get config value with precedence:
    // 1. Environment variable
    // 2. .env file
    // 3. Default value
    const getValue = (key: string, defaultValue: string): string => {
      return Deno.env.get(key) || dotEnvConfig[key] || defaultValue;
    };

    // Helper function to get optional config value
    const getOptionalValue = (key: string): string | undefined => {
      return Deno.env.get(key) || dotEnvConfig[key];
    };

    // Build the configuration object
    const config: AppConfig = {
      core: {
        dataDir: getValue("LENS_DATA_DIR", defaultDataDir()),
        logLevel: (getValue("LENS_LOG_LEVEL", "info") as "debug" | "info" | "warn" | "error"),
        port: parseInt(getValue("LENS_PORT", "8000")),
      },
      llm: {
        ollamaBaseUrl: getValue("LENS_OLLAMA_BASE_URL", "http://localhost:11434"),
        embeddingModel: getValue("LENS_OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
        llmModel: getValue("LENS_OLLAMA_LLM_MODEL", "llama2"),
      },
      langChain: {
        tracing: getValue("LENS_LANGCHAIN_TRACING", "false") === "true",
      },
      langSmith: {
        apiKey: getValue("LENS_LANGSMITH_API_KEY", ""),
        project: getValue("LENS_LANGSMITH_PROJECT", "lens-development"),
        tracingEnabled: getValue("LENS_LANGSMITH_TRACING_ENABLED", "true") === "true",
      },
      database: {
        dbPath: getValue("LENS_DB_PATH", join(defaultDataDir(), "lens.db")),
        vectorDbUrl: getOptionalValue("LENS_VECTOR_DB_URL"),
      },
    };

    // Validate the configuration
    return validateConfig(config);
  } catch (error) {
    const errorMessage = error instanceof Error
      ? error.message
      : String(error);
    return Err(new ConfigError(`Failed to load configuration: ${errorMessage}`));
  }
}

/**
 * Validate the configuration
 */
export function validateConfig(config: AppConfig): Result<AppConfig, ConfigError> {
  // Define required values that must be present
  const requiredValues = [
    { name: "LangSmith API Key", value: config.langSmith.apiKey },
  ];

  const missing = requiredValues.filter(item => !item.value || item.value.trim() === "");

  if (missing.length > 0) {
    const missingNames = missing.map(item => item.name).join(", ");
    return Err(new ConfigError(
      `Missing required configuration: ${missingNames}. Please check your .env file or environment variables.`
    ));
  }

  return Ok(config);
}

// Export a function to get the configuration
// This is a function rather than a constant to allow for testing and mocking
export async function getConfig(): Promise<AppConfig> {
  const configResult = await loadConfig();

  if (configResult.isErr()) {
    console.error(configResult.unwrapErr().message);
    Deno.exit(1);
  }

  return configResult.unwrap();
}
