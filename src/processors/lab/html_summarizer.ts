/**
 * HTML Content Summarizer Lab
 *
 * This module provides functionality to extract text from HTML files,
 * summarize the content using Ollama, and save the processed results.
 *
 * It uses a functional programming approach with pure functions and composition.
 *
 * Key features:
 * 1. Extract text content from HTML files
 * 2. Summarize content using Ollama
 * 3. Save processed content to files
 * 4. Process HTML files in a single operation
 */

import { join } from "https://deno.land/std@0.224.0/path/mod.ts";
import { ensureDir } from "https://deno.land/std@0.224.0/fs/ensure_dir.ts";
import { ChatOllama } from "@langchain/community/chat_models/ollama";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { getConfig } from "../../config/mod.ts";

// ============================================================================
// Types
// ============================================================================

/**
 * Options for summarizing content
 */
export interface SummaryOptions {
  /** The Ollama model to use */
  modelName?: string;
  /** The Ollama API base URL */
  baseUrl?: string;
  /** The temperature for generation (0.0-1.0) */
  temperature?: number;
  /** Whether to enable LangSmith tracing */
  langSmithTracing?: boolean;
  /** LangSmith API key (if not using config) */
  langSmithApiKey?: string;
  /** LangSmith project name (if not using config) */
  langSmithProject?: string;
}

/**
 * Response from the summarization function
 */
export interface SummaryResponse {
  success: boolean;
  content?: string;
  error?: string;
}

/**
 * Options for processing an HTML file
 */
export interface ProcessOptions extends SummaryOptions {
  /** The input file path */
  inputPath: string;
  /** The output directory */
  outputDir: string;
  /** Whether to overwrite existing files */
  overwrite?: boolean;
}

// ============================================================================
// HTML Processing Functions
// ============================================================================

/**
 * Extract text content from HTML
 *
 * This function extracts the main text content from HTML, focusing on
 * paragraphs, headings, and other text elements while removing navigation,
 * sidebars, and other non-content elements.
 *
 * @param html The HTML content to process
 * @returns The extracted text content
 */
export function extractTextFromHtml(html: string): string {
  // Simple extraction of text from HTML
  // This is a basic implementation for lab purposes
  // A more robust solution would use a proper HTML parser

  try {
    // Remove script and style elements
    let text = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, " ");
    text = text.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, " ");

    // Extract content from body if present
    const bodyMatch = text.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
    if (bodyMatch && bodyMatch[1]) {
      text = bodyMatch[1];
    }

    // Remove HTML tags but preserve content
    // First, replace specific tags that shouldn't add spaces
    text = text.replace(/<(strong|em|b|i|span)[^>]*>/gi, "");
    text = text.replace(/<\/(strong|em|b|i|span)[^>]*>/gi, "");

    // Then replace other tags with spaces
    text = text.replace(/<[^>]+>/g, " ");

    // Normalize whitespace
    text = text.replace(/\s+/g, " ");

    // Decode HTML entities
    text = text.replace(/&nbsp;/g, " ");
    text = text.replace(/&amp;/g, "&");
    text = text.replace(/&lt;/g, "<");
    text = text.replace(/&gt;/g, ">");
    text = text.replace(/&quot;/g, "\"");
    text = text.replace(/&#39;/g, "'");

    // Whitespace already normalized above

    // Trim the text
    text = text.trim();

    return text;
  } catch (error) {
    console.error("Error extracting text from HTML:", error);
    return "";
  }
}

// ============================================================================
// Ollama Integration Functions
// ============================================================================

/**
 * Summarize content using Ollama
 *
 * This function sends content to Ollama for summarization using LangChain.
 *
 * @param content The content to summarize
 * @param options Options for the summarization
 * @returns Object with success status and either summary content or error message
 */
export async function summarizeContent(
  content: string,
  options: SummaryOptions = {}
): Promise<SummaryResponse> {
  try {
    // If LangSmith tracing is explicitly disabled, skip config loading
    if (options.langSmithTracing === false) {
      // Explicitly disable tracing
      Deno.env.set("LANGCHAIN_TRACING_V2", "false");
    } else {
      try {
        // Configure LangSmith tracing
        const config = await getConfig();

        // Use either provided options or config values
        const apiKey = options.langSmithApiKey || config.langSmith.apiKey;
        const project = options.langSmithProject || config.langSmith.project;

        if (apiKey) {
          Deno.env.set("LANGCHAIN_API_KEY", apiKey);
          Deno.env.set("LANGCHAIN_PROJECT", project);
          Deno.env.set("LANGCHAIN_TRACING_V2", "true");
        }
      } catch (_configError) {
        // If config loading fails but tracing isn't explicitly disabled,
        // disable it and continue
        console.warn("Failed to load LangSmith config, disabling tracing");
        Deno.env.set("LANGCHAIN_TRACING_V2", "false");
      }
    }

    // Create the chat model
    const model = new ChatOllama({
      baseUrl: options.baseUrl || "http://localhost:11434",
      model: options.modelName || "llama3.2",
      temperature: options.temperature || 0.7,
    });

    // Create a prompt template
    const prompt = ChatPromptTemplate.fromMessages([
      ["system", `You are a helpful assistant that summarizes content.
      Create a concise but comprehensive summary of the provided text.
      Focus on the main points, key arguments, and important details.
      Organize the summary in a clear, readable format with paragraphs.
      Do not include your own opinions or analysis.`],
      ["human", `Please summarize the following content:\n\n${content}`],
    ]);

    // Create the chain
    const chain = prompt.pipe(model).pipe(new StringOutputParser());

    // Invoke the chain
    const summary = await chain.invoke({});

    return {
      success: true,
      content: summary,
    };
  } catch (error: unknown) {
    const errorMessage = error instanceof Error
      ? error.message
      : String(error);

    return {
      success: false,
      error: `Failed to summarize content: ${errorMessage}`
    };
  }
}

// ============================================================================
// File Operations Functions
// ============================================================================

/**
 * Save processed content to a file
 *
 * @param content The content to save
 * @param outputPath The path to save the content to
 * @param overwrite Whether to overwrite existing files
 * @returns Promise that resolves when the content is saved
 */
export async function saveProcessedContent(
  content: string,
  outputPath: string,
  overwrite: boolean = false
): Promise<void> {
  try {
    // Check if file exists and we're not overwriting
    if (!overwrite) {
      try {
        const stat = await Deno.stat(outputPath);
        if (stat.isFile) {
          console.log(`File already exists: ${outputPath} (skipping)`);
          return;
        }
      } catch (_error) {
        // File doesn't exist, which is fine
      }
    }

    // Ensure the directory exists
    await ensureDir(outputPath.substring(0, outputPath.lastIndexOf("/")));

    // Write the content to the file
    await Deno.writeTextFile(outputPath, content);

    console.log(`Content saved to: ${outputPath}`);
  } catch (error) {
    throw new Error(`Error saving content: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Create an output filename from an input path
 *
 * @param inputPath The input file path
 * @returns The output filename
 */
export function createOutputFilename(inputPath: string): string {
  // Get the base filename without extension
  const filename = inputPath.split("/").pop() || "unknown";
  const baseFilename = filename.replace(/\.[^/.]+$/, "");

  // Create the output filename
  return `${baseFilename}-summary.md`;
}

// ============================================================================
// Main Processing Function
// ============================================================================

/**
 * Process an HTML file: extract text, summarize, and save
 *
 * @param options Options for processing the HTML file
 * @returns Object with success status and either summary content or error message
 */
export async function processHtmlFile(
  options: ProcessOptions
): Promise<SummaryResponse> {
  try {
    // Read the HTML file
    const html = await Deno.readTextFile(options.inputPath);

    // Extract text from HTML
    const text = extractTextFromHtml(html);

    // Summarize the content
    const summary = await summarizeContent(text, {
      modelName: options.modelName,
      baseUrl: options.baseUrl,
      temperature: options.temperature,
      langSmithTracing: options.langSmithTracing,
      langSmithApiKey: options.langSmithApiKey,
      langSmithProject: options.langSmithProject,
    });

    // If summarization failed, return the error
    if (!summary.success) {
      return summary;
    }

    // Create the output filename
    const outputFilename = createOutputFilename(options.inputPath);
    const outputPath = join(options.outputDir, outputFilename);

    // Save the processed content
    await saveProcessedContent(summary.content!, outputPath, options.overwrite);

    return {
      success: true,
      content: summary.content,
    };
  } catch (error: unknown) {
    const errorMessage = error instanceof Error
      ? error.message
      : String(error);

    return {
      success: false,
      error: `Failed to process HTML file: ${errorMessage}`
    };
  }
}

// ============================================================================
// Example Usage
// ============================================================================

// Example usage when run directly
if (import.meta.main) {
  console.log("HTML Content Summarizer");

  try {
    // Process the specified HTML file with LangSmith tracing enabled
    const result = await processHtmlFile({
      inputPath: "./tmp/data/fetched/on-reading-novels.html",
      outputDir: "./tmp/data/processed",
      modelName: "llama3.2",
      temperature: 0.5,
      langSmithTracing: true, // Enable LangSmith tracing using config values
    });

    if (result.success) {
      console.log("✅ Successfully processed HTML file");
      console.log("Summary:", result.content);
    } else {
      console.error("❌ Failed to process HTML file:", result.error);
    }
  } catch (error) {
    console.error("Error:", error instanceof Error ? error.message : String(error));
  }
}
