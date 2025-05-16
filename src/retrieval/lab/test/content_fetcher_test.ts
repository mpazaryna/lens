/**
 * Tests for the Content Fetcher module
 *
 * This module contains tests for the content fetcher functionality.
 * It tests the core functions for fetching and saving content from URLs.
 *
 * The tests use mocks to avoid making actual network requests during testing.
 */

import { assertEquals, assertExists } from "https://deno.land/std@0.224.0/assert/mod.ts";
import {
  createFilenameFromUrl,
  extractUrls,
  fetchContent,
  sanitizeFilename,
} from "../content_fetcher.ts";

// Sample HTML content for testing
const SAMPLE_HTML = `
<!DOCTYPE html>
<html>
<head>
  <title>Test Page</title>
</head>
<body>
  <h1>Test Content</h1>
  <p>This is a test page for the content fetcher.</p>
</body>
</html>
`;

// Sample JSON data for testing
const SAMPLE_JSON = {
  title: "Test Feed",
  link: "https://example.com",
  items: [
    {
      title: "Test Article 1",
      link: "https://example.com/article1",
      pubDate: "2025-05-01",
    },
    {
      title: "Test Article 2",
      link: "https://example.com/article2",
      pubDate: "2025-05-02",
    },
  ],
};

// Mock fetch function for testing
const originalFetch = globalThis.fetch;
const mockFetch = (response: string, ok = true, status = 200) => {
  globalThis.fetch = () => {
    return Promise.resolve({
      ok,
      status,
      statusText: ok ? "OK" : "Error",
      text: () => Promise.resolve(response),
    } as Response);
  };
};

// Restore original fetch after tests
const restoreFetch = () => {
  globalThis.fetch = originalFetch;
};

Deno.test("sanitizeFilename - should sanitize filenames correctly", () => {
  assertEquals(sanitizeFilename("test file.txt"), "test_file.txt");
  assertEquals(sanitizeFilename("test/file.txt"), "test_file.txt");
  assertEquals(sanitizeFilename("test\\file.txt"), "test_file.txt");
  assertEquals(sanitizeFilename("test?file.txt"), "test_file.txt");
  assertEquals(sanitizeFilename("test:file.txt"), "test_file.txt");
  assertEquals(sanitizeFilename("test*file.txt"), "test_file.txt");
  assertEquals(sanitizeFilename("test|file.txt"), "test_file.txt");
  assertEquals(sanitizeFilename("test\"file.txt"), "test_file.txt");
  assertEquals(sanitizeFilename("test<file.txt"), "test_file.txt");
  assertEquals(sanitizeFilename("test>file.txt"), "test_file.txt");
  assertEquals(sanitizeFilename("TEST FILE.TXT"), "test_file.txt");
});

Deno.test("createFilenameFromUrl - should create filenames from URLs correctly", () => {
  assertEquals(createFilenameFromUrl("https://example.com/article"), "article.html");
  assertEquals(createFilenameFromUrl("https://example.com/article/"), "article.html");
  assertEquals(createFilenameFromUrl("https://example.com/path/to/article"), "article.html");
  assertEquals(createFilenameFromUrl("https://example.com"), "example.com.html");
  assertEquals(createFilenameFromUrl("https://example.com/article?param=value"), "article.html");
  assertEquals(createFilenameFromUrl("https://example.com/article#section"), "article.html");
  assertEquals(createFilenameFromUrl("https://example.com/article-with-dashes"), "article-with-dashes.html");
  assertEquals(createFilenameFromUrl("https://example.com/article_with_underscores"), "article_with_underscores.html");
});

Deno.test("fetchContent - should fetch content successfully", async () => {
  mockFetch(SAMPLE_HTML);

  try {
    const result = await fetchContent({ url: "https://example.com/article" });
    assertEquals(result, SAMPLE_HTML);
  } finally {
    restoreFetch();
  }
});

Deno.test("fetchContent - should handle fetch errors", async () => {
  mockFetch("Not Found", false, 404);

  try {
    let error;
    try {
      await fetchContent({ url: "https://example.com/not-found" });
    } catch (e) {
      error = e;
    }
    assertExists(error);
    assertEquals(
      (error as Error).message.includes("Failed to fetch content: 404"),
      true
    );
  } finally {
    restoreFetch();
  }
});

Deno.test("extractUrls - should extract URLs from JSON data", () => {
  const urls = extractUrls(SAMPLE_JSON);
  assertEquals(urls, [
    "https://example.com/article1",
    "https://example.com/article2",
  ]);
});

Deno.test("extractUrls - should handle empty or invalid data", () => {
  assertEquals(extractUrls({}), []);
  assertEquals(extractUrls({ items: [] }), []);
  assertEquals(extractUrls({ items: [{ title: "No Link" }] }), []);
});
