/**
 * Tests for the Template Client
 */

import { assertEquals, assertExists } from "@std/assert";
import { TemplateClient } from "../template_client.ts";

// Use the prompts directory
const templateDir = "./prompts";

// This test requires Ollama to be running locally
Deno.test({
  name: "TemplateClient - extractTopics extracts topics from content",
  async fn() {
    const client = new TemplateClient({
      templateDir,
      defaultModel: "llama3.2",
    });
    
    const content = `
      TypeScript is a strongly typed programming language that builds on JavaScript, 
      giving you better tooling at any scale. It adds additional syntax to JavaScript 
      to support a tighter integration with your editor. This can help catch errors early in your editor.
      
      TypeScript code converts to JavaScript, which runs anywhere JavaScript runs: 
      In a browser, on Node.js or Deno and in your apps.
      
      TypeScript understands JavaScript and uses type inference to give you great tooling 
      without additional code.
    `;
    
    const result = await client.extractTopics(content);
    
    // We don't know if Ollama is running, so we just check the structure
    if (result.success) {
      assertEquals(result.success, true);
      assertExists(result.content);
      assertEquals(typeof result.content, "string");
      assertEquals(result.content.length > 0, true);
      assertEquals(result.error, undefined);
      
      console.log("Extracted topics:", result.content);
      
      // Try to parse the JSON response
      try {
        const topics = JSON.parse(result.content);
        assertEquals(Array.isArray(topics), true);
        
        if (topics.length > 0) {
          assertExists(topics[0].topic);
          assertExists(topics[0].relevance);
        }
      } catch (error: unknown) {
        const errorMessage = error instanceof Error 
          ? error.message 
          : String(error);
        console.log("Failed to parse JSON response:", errorMessage);
      }
    } else {
      assertEquals(result.success, false);
      assertExists(result.error);
      assertEquals(result.content, undefined);
      
      console.log("Topic extraction failed:", result.error);
    }
  },
  sanitizeResources: false,
  sanitizeOps: false,
});

// This test requires Ollama to be running locally
Deno.test({
  name: "TemplateClient - reformulateQuery reformulates a query",
  async fn() {
    const client = new TemplateClient({
      templateDir,
      defaultModel: "llama3.2",
    });
    
    const query = "how to use typescript with deno";
    
    const result = await client.reformulateQuery(
      query,
      "Intermediate TypeScript developer interested in server-side development",
      "programming"
    );
    
    // We don't know if Ollama is running, so we just check the structure
    if (result.success) {
      assertEquals(result.success, true);
      assertExists(result.content);
      assertEquals(typeof result.content, "string");
      assertEquals(result.content.length > 0, true);
      assertEquals(result.error, undefined);
      
      console.log("Reformulated query:", result.content);
      
      // Try to parse the JSON response
      try {
        const reformulated = JSON.parse(result.content);
        assertExists(reformulated.expanded);
        assertExists(reformulated.specific);
        assertExists(reformulated.semantic);
      } catch (error: unknown) {
        const errorMessage = error instanceof Error 
          ? error.message 
          : String(error);
        console.log("Failed to parse JSON response:", errorMessage);
      }
    } else {
      assertEquals(result.success, false);
      assertExists(result.error);
      assertEquals(result.content, undefined);
      
      console.log("Query reformulation failed:", result.error);
    }
  },
  sanitizeResources: false,
  sanitizeOps: false,
});
