import { assertEquals, assertExists } from "@std/assert";
import { chatWithOllama } from "@src/labs/langchain_ollama.ts";

Deno.test({
  name: "chatWithOllama - simple message test",
  async fn() {
    // This test requires Ollama to be running locally
    const result = await chatWithOllama("Hello, how are you?");
    
    // We don't know if Ollama is running, so we just check the structure
    if (result.success) {
      assertEquals(result.success, true);
      assertExists(result.content);
      assertEquals(typeof result.content, "string");
      assertEquals(result.content.length > 0, true);
      assertEquals(result.error, undefined);
      
      console.log("Ollama response:", result.content?.substring(0, 100) + "...");
    } else {
      assertEquals(result.success, false);
      assertExists(result.error);
      assertEquals(result.content, undefined);
      
      console.log("Ollama chat failed:", result.error);
    }
  },
  sanitizeResources: false,
  sanitizeOps: false,
});
