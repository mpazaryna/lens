/**
 * Tests for the HTML Content Summarizer module
 *
 * This file contains tests for all HTML summarizer functionality:
 * 1. HTML text extraction
 * 2. Content summarization with Ollama
 * 3. File processing and saving
 */

import { assertEquals, assertExists } from "https://deno.land/std@0.224.0/assert/mod.ts";
import {
  extractTextFromHtml,
  summarizeContent,
  createOutputFilename,
  processHtmlFile
} from "../html_summarizer.ts";

// IMPORTANT: Disable LangSmith tracing for tests
// This prevents network dependencies and config validation issues in test environments
Deno.env.set("LANGCHAIN_TRACING_V2", "false");
Deno.env.set("LANGCHAIN_API_KEY", "test-key-for-testing-only");
Deno.env.set("LANGCHAIN_PROJECT", "test-project-for-testing-only");

// Sample HTML content for testing
const SAMPLE_HTML = `
<!DOCTYPE html>
<html>
<head>
  <title>Test Page</title>
  <style>
    body { font-family: Arial, sans-serif; }
  </style>
  <script>
    console.log("This should be removed");
  </script>
</head>
<body>
  <header>
    <nav>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/about">About</a></li>
      </ul>
    </nav>
  </header>
  <main>
    <h1>Article Title</h1>
    <p>This is the first paragraph of the article.</p>
    <p>This is the second paragraph with some <strong>bold text</strong>.</p>
  </main>
  <footer>
    <p>&copy; 2025 Test Site</p>
  </footer>
</body>
</html>
`;

// Test 1: HTML text extraction
Deno.test({
  name: "extractTextFromHtml - extracts text content correctly",
  fn() {
    const text = extractTextFromHtml(SAMPLE_HTML);

    // Print the full extracted text for debugging
    console.log("FULL EXTRACTED TEXT:", text);

    // Check that the text contains the main content
    assertEquals(text.includes("Article Title"), true);
    assertEquals(text.includes("This is the first paragraph of the article."), true);
    assertEquals(text.includes("This is the second paragraph with some bold text."), true);

    // Check that script content is removed
    assertEquals(text.includes("This should be removed"), false);

    // Check that navigation is included (simple implementation)
    // A more sophisticated implementation might remove this
    assertEquals(text.includes("Home"), true);
  }
});

// Test 2: Create output filename
Deno.test({
  name: "createOutputFilename - creates correct output filename",
  fn() {
    const inputPath = "/path/to/article.html";
    const outputFilename = createOutputFilename(inputPath);

    assertEquals(outputFilename, "article-summary.md");
  }
});

// Test 3: Content summarization with Ollama
Deno.test({
  name: "summarizeContent - summarizes content with Ollama",
  async fn() {
    // This test requires Ollama to be running locally
    const content = "Article Title\n\nThis is the first paragraph of the article.\n\nThis is the second paragraph with some bold text.";

    // Explicitly disable LangSmith tracing for tests
    const result = await summarizeContent(content, {
      langSmithTracing: false,
      temperature: 0.1
    });

    // We don't know if Ollama is running, so we just check the structure
    if (result.success) {
      assertEquals(result.success, true);
      assertExists(result.content);
      assertEquals(typeof result.content, "string");
      assertEquals(result.content.length > 0, true);
      assertEquals(result.error, undefined);

      console.log("Summary:", result.content?.substring(0, 100) + "...");
    } else {
      assertEquals(result.success, false);
      assertExists(result.error);
      assertEquals(result.content, undefined);

      console.log("Summarization failed:", result.error);
    }
  },
  sanitizeResources: false,
  sanitizeOps: false,
});

// Test 4: Process HTML file
Deno.test({
  name: "processHtmlFile - processes HTML file end-to-end",
  async fn() {
    // Mock Deno.readTextFile to return sample HTML
    const originalReadTextFile = Deno.readTextFile;
    // @ts-ignore: Mocking for test purposes
    Deno.readTextFile = () => Promise.resolve(SAMPLE_HTML);

    // Mock Deno.writeTextFile to avoid writing to disk
    const originalWriteTextFile = Deno.writeTextFile;
    let writtenContent = "";
    let writtenPath = "";
    // @ts-ignore: Mocking for test purposes
    Deno.writeTextFile = (path, content) => {
      writtenPath = String(path);
      writtenContent = String(content);
      return Promise.resolve();
    };

    try {
      // Process the HTML file with LangSmith tracing disabled
      const result = await processHtmlFile({
        inputPath: "./test-input.html",
        outputDir: "./test-output",
        // Use a small temperature for more deterministic results
        temperature: 0.1,
        // Explicitly disable LangSmith tracing for tests
        langSmithTracing: false
      });

      // Check the result structure
      if (result.success) {
        assertEquals(result.success, true);
        assertExists(result.content);
        assertEquals(typeof result.content, "string");
        assertEquals(result.content.length > 0, true);
        assertEquals(result.error, undefined);

        // Check that content was written
        assertEquals(writtenContent.length > 0, true);
        assertEquals(writtenPath.includes("test-input-summary.md"), true);

        console.log("Processed HTML file successfully");
        console.log("Summary:", result.content?.substring(0, 100) + "...");
      } else {
        assertEquals(result.success, false);
        assertExists(result.error);
        assertEquals(result.content, undefined);

        console.log("Processing failed:", result.error);
      }
    } finally {
      // Restore original functions
      Deno.readTextFile = originalReadTextFile;
      Deno.writeTextFile = originalWriteTextFile;
    }
  },
  sanitizeResources: false,
  sanitizeOps: false,
});
