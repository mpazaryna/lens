/**
 * LangChain integration with Ollama using the application configuration system.
 * This module provides a function to send a prompt to an Ollama model using LangChain
 * with configuration loaded from the .env file and environment variables.
 */

import { ChatOllama } from "@langchain/community/chat_models/ollama";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { getConfig } from "@src/config/mod.ts";

/**
 * Response from the chat function
 */
export interface ChatResponse {
  success: boolean;
  content?: string;
  error?: string;
}

/**
 * Send a simple chat message to Ollama using LangChain with configuration from the config system
 * 
 * @param message The user message to send
 * @returns Object with success status and either response content or error message
 */
export async function chatWithOllamaConfig(
  message: string
): Promise<ChatResponse> {
  try {
    // Load configuration
    const config = await getConfig();
    
    // Create the chat model using configuration values
    const model = new ChatOllama({
      baseUrl: config.llm.ollamaBaseUrl,
      model: config.llm.llmModel,
      temperature: 0.7,
    });

    // Create a simple prompt template
    const prompt = ChatPromptTemplate.fromMessages([
      ["system", "You are a helpful AI assistant."],
      ["human", "{input}"],
    ]);

    // Create the chain
    const chain = prompt.pipe(model).pipe(new StringOutputParser());

    // Invoke the chain with the user message
    const response = await chain.invoke({
      input: message,
    });

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
      error: `Failed to chat with Ollama: ${errorMessage}`
    };
  }
}

// Example usage when run directly
if (import.meta.main) {
  console.log("Testing Ollama chat with config...");
  const result = await chatWithOllamaConfig("Hello, how are you?");
  
  if (result.success) {
    console.log("✅ Successfully chatted with Ollama");
    console.log("Response:", result.content);
  } else {
    console.error("❌ Failed to chat with Ollama:", result.error);
  }
}
