/**
 * Simple Ollama API validation test.
 * Checks if we can connect to the Ollama API and retrieve model list.
 */

/**
 * Validates connection to Ollama API
 * @param baseUrl The Ollama API base URL
 * @returns Object with success status and either model list or error message
 */
export async function validateOllamaConnection(
  baseUrl: string = "http://localhost:11434"
): Promise<{ success: boolean; data?: string[]; error?: string }> {
  try {
    const response = await fetch(`${baseUrl}/api/tags`);
    
    if (!response.ok) {
      return {
        success: false,
        error: `HTTP error ${response.status}: ${response.statusText}`
      };
    }
    
    const data = await response.json();
    return {
      success: true,
      data: data.models?.map((model: { name: string }) => model.name) || []
    };
  } catch (error: unknown) {
    const errorMessage = error instanceof Error 
      ? error.message 
      : String(error);
      
    return {
      success: false,
      error: `Failed to connect to Ollama: ${errorMessage}`
    };
  }
}

// Example usage when run directly
if (import.meta.main) {
  console.log("Testing Ollama connection...");
  const result = await validateOllamaConnection();
  
  if (result.success) {
    console.log("✅ Successfully connected to Ollama");
    console.log("Available models:", result.data);
  } else {
    console.error("❌ Failed to connect to Ollama:", result.error);
  }
}
