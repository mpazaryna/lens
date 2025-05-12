/**
 * Unit tests for the configuration module.
 */

import { assertEquals, assertStringIncludes } from "@std/assert";
import { assertExists } from "@std/assert";
import { join } from "@std/path";
import {
  loadConfig,
  validateConfig,
  defaultDataDir,
  AppConfig
} from "@src/config.ts";

// Helper to set environment variables for testing
async function withEnv(
  env: Record<string, string>,
  fn: () => Promise<void> | void
): Promise<void> {
  const originalEnv: Record<string, string | undefined> = {};

  // Save original env values and set new ones
  for (const [key, value] of Object.entries(env)) {
    originalEnv[key] = Deno.env.get(key);
    if (value === "") {
      Deno.env.delete(key);
    } else {
      Deno.env.set(key, value);
    }
  }

  try {
    const result = fn();
    if (result instanceof Promise) {
      await result;
    }
  } finally {
    // Restore original env values
    for (const [key, value] of Object.entries(originalEnv)) {
      if (value === undefined) {
        Deno.env.delete(key);
      } else {
        Deno.env.set(key, value);
      }
    }
  }
}

Deno.test("defaultDataDir returns platform-specific path", () => {
  const homeDir = Deno.env.get("HOME") || Deno.env.get("USERPROFILE") || ".";
  const dataDir = defaultDataDir();

  // Just test that it returns a string and includes the home directory
  assertExists(dataDir);
  assertStringIncludes(dataDir, homeDir);
});

Deno.test("validateConfig returns error for missing required values", () => {
  const config: AppConfig = {
    core: {
      dataDir: "/tmp/lens",
      logLevel: "info",
      port: 8000,
    },
    llm: {
      ollamaBaseUrl: "http://localhost:11434",
      embeddingModel: "nomic-embed-text",
      llmModel: "llama2",
    },
    langChain: {
      tracing: false,
    },
    langSmith: {
      apiKey: "", // Missing required value
      project: "lens-test",
      tracingEnabled: true,
    },
    database: {
      dbPath: "/tmp/lens/lens.db",
    },
  };

  const result = validateConfig(config);
  assertEquals(result.isErr(), true);

  if (result.isErr()) {
    const error = result.unwrapErr();
    assertStringIncludes(error.message, "LangSmith API Key");
  }
});

Deno.test("validateConfig returns Ok for valid config", () => {
  const config: AppConfig = {
    core: {
      dataDir: "/tmp/lens",
      logLevel: "info",
      port: 8000,
    },
    llm: {
      ollamaBaseUrl: "http://localhost:11434",
      embeddingModel: "nomic-embed-text",
      llmModel: "llama2",
    },
    langChain: {
      tracing: false,
    },
    langSmith: {
      apiKey: "test-api-key", // Valid value
      project: "lens-test",
      tracingEnabled: true,
    },
    database: {
      dbPath: "/tmp/lens/lens.db",
    },
  };

  const result = validateConfig(config);
  assertEquals(result.isOk(), true);

  if (result.isOk()) {
    const validConfig = result.unwrap();
    assertEquals(validConfig, config);
  }
});

Deno.test("loadConfig loads from environment variables", async () => {
  await withEnv({
    LENS_DATA_DIR: "/custom/data/dir",
    LENS_PORT: "9000",
    LENS_LANGSMITH_API_KEY: "test-api-key",
    LENS_LANGSMITH_PROJECT: "custom-project",
  }, async () => {
    const result = await loadConfig();

    // Check that the result is Ok
    if (!result.isOk()) {
      console.error("Expected Ok result, got Err:", result.unwrapErr().message);
    }
    assertEquals(result.isOk(), true);

    if (result.isOk()) {
      const config = result.unwrap();
      assertEquals(config.core.dataDir, "/custom/data/dir");
      assertEquals(config.core.port, 9000);
      assertEquals(config.langSmith.apiKey, "test-api-key");
      assertEquals(config.langSmith.project, "custom-project");

      // Check defaults for values not specified
      assertEquals(config.core.logLevel, "info");
      assertEquals(config.llm.ollamaBaseUrl, "http://localhost:11434");
    }
  });
});

Deno.test("loadConfig returns error for missing required values", async () => {
  // Create a temporary directory without a .env file
  const tempDir = await Deno.makeTempDir();
  const originalCwd = Deno.cwd();
  
  try {
    // Change to the temp directory to avoid loading any .env file
    Deno.chdir(tempDir);
    
    // Clear all relevant environment variables
    await withEnv({
      LENS_LANGSMITH_API_KEY: "", // Explicitly set to empty
      LENS_DATA_DIR: "/tmp/lens", // Set other required values
      LENS_PORT: "8000",
      LENS_LOG_LEVEL: "info",
      LENS_OLLAMA_BASE_URL: "http://localhost:11434",
      LENS_OLLAMA_EMBEDDING_MODEL: "nomic-embed-text",
      LENS_OLLAMA_LLM_MODEL: "llama2",
      LENS_LANGCHAIN_TRACING: "false",
      LENS_LANGSMITH_PROJECT: "lens-test",
      LENS_LANGSMITH_TRACING_ENABLED: "true",
      LENS_DB_PATH: "/tmp/lens/lens.db",
      LENS_VECTOR_DB_URL: "",
    }, async () => {
      const result = await loadConfig();
      assertEquals(result.isErr(), true);

      if (result.isErr()) {
        const error = result.unwrapErr();
        assertStringIncludes(error.message, "LangSmith API Key");
      }
    });
  } finally {
    // Restore original directory
    Deno.chdir(originalCwd);
    
    // Clean up
    await Deno.remove(tempDir, { recursive: true });
  }
});

// This test requires temporarily writing a .env file
Deno.test("loadConfig loads from .env file", async () => {
  const tempDir = await Deno.makeTempDir();
  const envPath = join(tempDir, ".env");

  try {
    // Create a temporary .env file with clean values (no whitespace)
    await Deno.writeTextFile(envPath,
`LENS_DATA_DIR=/env/file/data/dir
LENS_PORT=7000
LENS_LANGSMITH_API_KEY=env-file-api-key
LENS_LANGSMITH_PROJECT=env-file-project`
    );

    // Set the .env file path (this is a hack for testing)
    const originalCwd = Deno.cwd();
    try {
      Deno.chdir(tempDir);

      // Clear any existing env vars that might interfere
      await withEnv({
        LENS_DATA_DIR: "",
        LENS_PORT: "",
        LENS_LANGSMITH_API_KEY: "",
        LENS_LANGSMITH_PROJECT: "",
      }, async () => {
        const result = await loadConfig();

        // Debug output if test fails
        if (!result.isOk()) {
          console.error("Expected Ok result, got Err:", result.unwrapErr().message);
        }
        assertEquals(result.isOk(), true);

        if (result.isOk()) {
          const config = result.unwrap();
          assertEquals(config.core.dataDir, "/env/file/data/dir");
          assertEquals(config.core.port, 7000);
          assertEquals(config.langSmith.apiKey, "env-file-api-key");
          assertEquals(config.langSmith.project, "env-file-project");
        }
      });
    } finally {
      Deno.chdir(originalCwd);
    }
  } finally {
    // Clean up
    await Deno.remove(tempDir, { recursive: true });
  }
});

Deno.test("Environment variables override .env file", async () => {
  const tempDir = await Deno.makeTempDir();
  const envPath = join(tempDir, ".env");

  try {
    // Create a temporary .env file with clean values (no whitespace)
    await Deno.writeTextFile(envPath,
`LENS_DATA_DIR=/env/file/data/dir
LENS_PORT=7000
LENS_LANGSMITH_API_KEY=env-file-api-key
LENS_LANGSMITH_PROJECT=env-file-project`
    );

    // Set the .env file path and override with env vars
    const originalCwd = Deno.cwd();
    try {
      Deno.chdir(tempDir);

      await withEnv({
        LENS_DATA_DIR: "/env/var/data/dir", // Override
        LENS_LANGSMITH_API_KEY: "env-var-api-key", // Override
      }, async () => {
        const result = await loadConfig();

        // Debug output if test fails
        if (!result.isOk()) {
          console.error("Expected Ok result, got Err:", result.unwrapErr().message);
        }
        assertEquals(result.isOk(), true);

        if (result.isOk()) {
          const config = result.unwrap();

          // These should be from env vars
          assertEquals(config.core.dataDir, "/env/var/data/dir");
          assertEquals(config.langSmith.apiKey, "env-var-api-key");

          // These should be from .env file
          assertEquals(config.core.port, 7000);
          assertEquals(config.langSmith.project, "env-file-project");
        }
      });
    } finally {
      Deno.chdir(originalCwd);
    }
  } finally {
    // Clean up
    await Deno.remove(tempDir, { recursive: true });
  }
});
