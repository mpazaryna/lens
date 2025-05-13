import { assertEquals, assertExists } from "@std/assert";
import { validateOllamaConnection } from "../ollama.ts";

Deno.test({
  name: "validateOllamaConnection - real connection test",
  async fn() {
    // This test requires Ollama to be running locally
    const result = await validateOllamaConnection();
    
    // We don't know if Ollama is running, so we just check the structure
    if (result.success) {
      assertEquals(result.success, true);
      assertExists(result.data);
      assertEquals(Array.isArray(result.data), true);
      assertEquals(result.error, undefined);
      
      console.log("Available Ollama models:", result.data);
    } else {
      assertEquals(result.success, false);
      assertExists(result.error);
      assertEquals(result.data, undefined);
      
      console.log("Ollama connection failed:", result.error);
    }
  },
  sanitizeResources: false,
  sanitizeOps: false,
});
