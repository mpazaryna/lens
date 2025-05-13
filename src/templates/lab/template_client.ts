/**
 * Template Client
 * 
 * This module provides a client for using templates with LLMs.
 * It integrates the template engine to provide a simple interface
 * for calling LLMs with templates.
 */

// No longer need path import since we're using the import map
import { ChatOllama } from "@langchain/community/chat_models/ollama";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { TemplateEngine, LLMOptions, LLMResponse } from "./template_engine.ts";

/**
 * Options for the Template Client
 */
export interface TemplateClientOptions {
  templateDir: string;
  baseUrl?: string;
  defaultModel?: string;
}

/**
 * Template Client
 * 
 * This class provides methods for using templates with LLMs.
 */
export class TemplateClient {
  private templateEngine: TemplateEngine;
  private baseUrl: string;
  private defaultModel: string;
  
  /**
   * Create a new Template Client
   * @param options Client options
   */
  constructor(options: TemplateClientOptions) {
    this.templateEngine = new TemplateEngine(options.templateDir);
    this.baseUrl = options.baseUrl || "http://localhost:11434";
    this.defaultModel = options.defaultModel || "llama3.2";
  }
  
  /**
   * Extract topics from content using a template
   * @param content The content to analyze
   * @param maxTopics Maximum number of topics to extract
   * @param format Output format (json or text)
   * @param options LLM options
   * @returns LLM response with extracted topics
   */
  async extractTopics(
    content: string,
    maxTopics: number = 5,
    format: "json" | "text" = "json",
    options: LLMOptions = {}
  ): Promise<LLMResponse> {
    try {
      // Create the chat model
      const model = new ChatOllama({
        baseUrl: options.baseUrl || this.baseUrl,
        model: options.modelName || this.defaultModel,
        temperature: options.temperature || 0.3, // Lower temperature for more deterministic results
      });
      
      // Load the template
      const templatePath = "content_analysis/topic_extraction.md";
      const templateContent = await this.templateEngine.loadTemplate(templatePath);
      
      // Parse the template
      const parsedTemplate = this.templateEngine.parseTemplate(templateContent);
      
      // Create a system prompt
      const systemPrompt = parsedTemplate.systemPrompt;
      
      // Create a user prompt
      let userPrompt = `Extract the main topics from the following content:

Content:
${content}

Extract up to ${maxTopics} topics that best represent the main themes of this content.

`;
      
      if (format === "json") {
        userPrompt += `Return the topics as a JSON array of objects with "topic" and "relevance" properties. The relevance should be a number between 0 and 1 indicating how central the topic is to the content.`;
      } else {
        userPrompt += `Return the topics as a simple comma-separated list.`;
      }
      
      // Create a prompt template
      const prompt = ChatPromptTemplate.fromMessages([
        ["system", systemPrompt],
        ["human", userPrompt],
      ]);
      
      // Create the chain
      const chain = prompt.pipe(model).pipe(new StringOutputParser());
      
      // Invoke the chain
      const response = await chain.invoke({});
      
      return {
        success: true,
        content: response,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : String(error);
        
      return {
        success: false,
        error: `Failed to extract topics: ${errorMessage}`,
      };
    }
  }
  
  /**
   * Reformulate a query using a template
   * @param query The original query
   * @param userContext Optional user context
   * @param domain Optional domain focus
   * @param options LLM options
   * @returns LLM response with reformulated query
   */
  async reformulateQuery(
    query: string,
    userContext?: string,
    domain?: string,
    options: LLMOptions = {}
  ): Promise<LLMResponse> {
    const variables: Record<string, unknown> = { query };
    
    if (userContext) {
      variables.user_context = userContext;
    }
    
    if (domain) {
      variables.domain = domain;
    }
    
    return await this.templateEngine.callLLMWithTemplate(
      "query_processing/query_reformulation.md",
      variables,
      {
        modelName: options.modelName || this.defaultModel,
        baseUrl: options.baseUrl || this.baseUrl,
        temperature: options.temperature || 0.5,
      }
    );
  }
  
  /**
   * Call a template with custom variables
   * @param templatePath Path to the template
   * @param variables Variables to use in the template
   * @param options LLM options
   * @returns LLM response
   */
  async callTemplate(
    templatePath: string,
    variables: Record<string, unknown>,
    options: LLMOptions = {}
  ): Promise<LLMResponse> {
    return await this.templateEngine.callLLMWithTemplate(
      templatePath,
      variables,
      {
        modelName: options.modelName || this.defaultModel,
        baseUrl: options.baseUrl || this.baseUrl,
        temperature: options.temperature !== undefined ? options.temperature : 0.7,
      }
    );
  }
}

// Example usage when run directly
if (import.meta.main) {
  // Use the prompts directory from the import map
  const templateDir = "./prompts";
  
  // Create a client
  const client = new TemplateClient({
    templateDir,
    defaultModel: "llama3.2",
  });
  
  // Example content for topic extraction
  const content = `
    TypeScript is a strongly typed programming language that builds on JavaScript, 
    giving you better tooling at any scale. It adds additional syntax to JavaScript 
    to support a tighter integration with your editor. This can help catch errors early in your editor.
    
    TypeScript code converts to JavaScript, which runs anywhere JavaScript runs: 
    In a browser, on Node.js or Deno and in your apps.
    
    TypeScript understands JavaScript and uses type inference to give you great tooling 
    without additional code.
  `;
  
  console.log("Testing topic extraction...");
  const topicsResult = await client.extractTopics(content);
  
  if (topicsResult.success) {
    console.log("✅ Successfully extracted topics");
    console.log("Topics:", topicsResult.content);
  } else {
    console.error("❌ Failed to extract topics:", topicsResult.error);
  }
  
  // Example query for reformulation
  const query = "how to use typescript with deno";
  
  console.log("\nTesting query reformulation...");
  const queryResult = await client.reformulateQuery(
    query,
    "Intermediate TypeScript developer interested in server-side development",
    "programming"
  );
  
  if (queryResult.success) {
    console.log("✅ Successfully reformulated query");
    console.log("Reformulated query:", queryResult.content);
  } else {
    console.error("❌ Failed to reformulate query:", queryResult.error);
  }
}
