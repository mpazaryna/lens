/**
 * Template Engine for LLM interactions
 *
 * This module provides functionality to load, process, and render templates
 * for LLM interactions. Templates are stored as markdown files with a specific
 * structure and can include variable placeholders and conditional logic.
 */

import { join } from "@std/path";
import { ChatOllama } from "@langchain/community/chat_models/ollama";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

/**
 * Options for LLM calls
 */
export interface LLMOptions {
  modelName?: string;
  baseUrl?: string;
  temperature?: number;
}

/**
 * Response from LLM calls
 */
export interface LLMResponse {
  success: boolean;
  content?: string;
  error?: string;
}

/**
 * Template sections extracted from a markdown template
 */
export interface TemplateContent {
  name: string;
  description: string;
  inputVariables: Record<string, string>;
  systemPrompt: string;
  userPrompt: string;
  outputFormat: string;
}

/**
 * Template Engine class that handles loading, processing, and rendering templates
 */
export class TemplateEngine {
  private templateDir: string;

  /**
   * Create a new TemplateEngine
   * @param templateDir Base directory for templates
   */
  constructor(templateDir: string) {
    this.templateDir = templateDir;
  }

  /**
   * Load a template from the filesystem
   * @param path Path to the template, relative to the template directory
   * @returns The template content as a string
   */
  async loadTemplate(path: string): Promise<string> {
    try {
      const fullPath = join(this.templateDir, path);
      return await Deno.readTextFile(fullPath);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error
        ? error.message
        : String(error);
      throw new Error(`Failed to load template at ${path}: ${errorMessage}`);
    }
  }

  /**
   * Parse a markdown template into sections
   * @param template The template content as a string
   * @returns Parsed template sections
   */
  parseTemplate(template: string): TemplateContent {
    // Split the template into sections based on markdown headers
    const sections = template.split(/^## /m);

    // Extract the template name from the first section
    const nameMatch = sections[0].match(/# Template: (.*?)$/m);
    const name = nameMatch ? nameMatch[1].trim() : "Unnamed Template";

    // Initialize the template content
    const content: TemplateContent = {
      name,
      description: "",
      inputVariables: {},
      systemPrompt: "",
      userPrompt: "",
      outputFormat: "",
    };

    // Process each section
    for (const section of sections) {
      if (!section.trim()) continue;

      const sectionLines = section.trim().split("\n");
      const sectionName = sectionLines[0].trim();
      const sectionContent = sectionLines.slice(1).join("\n").trim();

      switch (sectionName) {
        case "Description": {
          content.description = sectionContent;
          break;
        }
        case "Input Variables": {
          // Parse input variables from list format
          const variableLines = sectionContent.split("\n");
          for (const line of variableLines) {
            const match = line.match(/- (.*?): (.*)/);
            if (match) {
              content.inputVariables[match[1].trim()] = match[2].trim();
            }
          }
          break;
        }
        case "System Prompt": {
          content.systemPrompt = sectionContent;
          break;
        }
        case "User Prompt": {
          content.userPrompt = sectionContent;
          break;
        }
        case "Output Format": {
          content.outputFormat = sectionContent;
          break;
        }
      }
    }

    return content;
  }

  /**
   * Process a template by handling conditional logic
   * @param template The template content
   * @param variables Variables to use for conditional evaluation
   * @returns Processed template with conditionals resolved
   */
  processTemplate(template: string, variables: Record<string, unknown>): string {
    // Simple implementation of conditional processing
    // This is a basic version that handles if/else blocks

    let processed = template;

    // Process if/else blocks
    const conditionalRegex = /{%\s*if\s+(.*?)\s*%}([\s\S]*?)(?:{%\s*else\s*%}([\s\S]*?))?{%\s*endif\s*%}/g;
    processed = processed.replace(conditionalRegex, (_, condition, ifContent, elseContent = "") => {
      // Evaluate the condition using the variables
      // This is a simple evaluation that checks if the variable exists and is truthy
      const parts = condition.split(/\s*==\s*/);
      let result: boolean;

      if (parts.length === 2) {
        // Handle equality comparison
        const varName = parts[0].trim();
        const value = parts[1].trim().replace(/^["']|["']$/g, ""); // Remove quotes
        result = String(variables[varName]) === value;
      } else {
        // Handle simple existence/truthiness check
        result = Boolean(variables[condition.trim()]);
      }

      return result ? ifContent : elseContent;
    });

    return processed;
  }

  /**
   * Render a template by substituting variables
   * @param template The processed template content
   * @param variables Variables to substitute into the template
   * @returns Rendered template with variables substituted
   */
  renderTemplate(template: string, variables: Record<string, unknown>): string {
    // Substitute variables in the template
    return template.replace(/{{(.*?)}}/g, (_, variableName) => {
      const name = variableName.trim();
      return variables[name] !== undefined ? String(variables[name]) : `{{${name}}}`;
    });
  }

  /**
   * Convert a template to a LangChain prompt template
   * @param templateContent Parsed template content
   * @returns LangChain ChatPromptTemplate
   */
  toLangChainTemplate(templateContent: TemplateContent): ChatPromptTemplate {
    return ChatPromptTemplate.fromMessages([
      ["system", templateContent.systemPrompt],
      ["human", templateContent.userPrompt],
    ]);
  }

  /**
   * Call an LLM with a rendered template
   * @param systemPrompt The system prompt
   * @param userPrompt The user prompt
   * @param options LLM options
   * @returns LLM response
   */
  async callLLM(
    systemPrompt: string,
    userPrompt: string,
    options: LLMOptions = {}
  ): Promise<LLMResponse> {
    try {
      // Create the chat model
      const model = new ChatOllama({
        baseUrl: options.baseUrl || "http://localhost:11434",
        model: options.modelName || "llama3.2",
        temperature: options.temperature || 0.7,
      });

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
    } catch (error) {
      const errorMessage = error instanceof Error
        ? error.message
        : String(error);

      return {
        success: false,
        error: `Failed to call LLM: ${errorMessage}`,
      };
    }
  }

  /**
   * Combined operation: load, parse, process, render, and call LLM with a template
   * @param path Path to the template
   * @param variables Variables to use in the template
   * @param options LLM options
   * @returns LLM response
   */
  async callLLMWithTemplate(
    path: string,
    variables: Record<string, unknown>,
    options: LLMOptions = {}
  ): Promise<LLMResponse> {
    try {
      // Load the template
      const templateContent = await this.loadTemplate(path);

      // Parse the template
      const parsedTemplate = this.parseTemplate(templateContent);

      // Process the template (handle conditionals)
      const processedSystemPrompt = this.processTemplate(parsedTemplate.systemPrompt, variables);
      const processedUserPrompt = this.processTemplate(parsedTemplate.userPrompt, variables);

      // Render the template (substitute variables)
      const renderedSystemPrompt = this.renderTemplate(processedSystemPrompt, variables);
      const renderedUserPrompt = this.renderTemplate(processedUserPrompt, variables);

      // Call the LLM
      return await this.callLLM(renderedSystemPrompt, renderedUserPrompt, options);
    } catch (error) {
      const errorMessage = error instanceof Error
        ? error.message
        : String(error);

      return {
        success: false,
        error: `Failed to process template: ${errorMessage}`,
      };
    }
  }
}
