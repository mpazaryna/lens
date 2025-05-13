/**
 * Tests for the Template Engine
 *
 * This module contains tests for the template engine functionality.
 * It tests the following features:
 * 1. Parsing templates into sections
 * 2. Processing templates with conditional logic
 * 3. Rendering templates by substituting variables
 * 4. Calling LLMs with rendered templates
 *
 * These tests ensure that the template engine works correctly and
 * can be used to create and use templates for LLM interactions.
 *
 * @module template_engine_test
 * @lab Tests for the experimental template engine
 * @version 0.1.0
 * @author Lens Team
 */

import { assertEquals, assertExists, assertStringIncludes } from "@std/assert";
import { TemplateEngine } from "../template_engine.ts";

// Use the prompts directory
const templateDir = "./prompts";

/**
 * Test: parseTemplate extracts sections correctly
 *
 * This test verifies that the parseTemplate function correctly extracts
 * all sections from a markdown template, including the name, description,
 * input variables, system prompt, user prompt, and output format.
 *
 * It creates a sample template with all sections and checks that each
 * section is correctly extracted and stored in the TemplateContent object.
 */
Deno.test({
  name: "TemplateEngine - parseTemplate extracts sections correctly",
  fn() {
    const engine = new TemplateEngine(templateDir);

    const template = `# Template: Test Template

## Description
This is a test template.

## Input Variables
- var1: First variable
- var2: Second variable

## System Prompt
System prompt content.

## User Prompt
User prompt with {{var1}} and {{var2}}.

## Output Format
Expected output format.`;

    const parsed = engine.parseTemplate(template);

    assertEquals(parsed.name, "Test Template");
    assertEquals(parsed.description, "This is a test template.");
    assertEquals(parsed.inputVariables.var1, "First variable");
    assertEquals(parsed.inputVariables.var2, "Second variable");
    assertEquals(parsed.systemPrompt, "System prompt content.");
    assertEquals(parsed.userPrompt, "User prompt with {{var1}} and {{var2}}.");
    assertEquals(parsed.outputFormat, "Expected output format.");
  }
});

/**
 * Test: processTemplate handles conditionals correctly
 *
 * This test verifies that the processTemplate function correctly processes
 * conditional logic in templates. It tests both simple conditionals and
 * equality comparisons.
 *
 * It creates a template with multiple conditional blocks and checks that
 * the correct content is included or excluded based on the variables.
 */
Deno.test({
  name: "TemplateEngine - processTemplate handles conditionals correctly",
  fn() {
    const engine = new TemplateEngine(templateDir);

    const template = `
    {% if condition1 %}
    This should be included.
    {% else %}
    This should not be included.
    {% endif %}

    {% if condition2 %}
    This should not be included.
    {% else %}
    This should be included.
    {% endif %}

    {% if format == "json" %}
    JSON format.
    {% else %}
    Text format.
    {% endif %}`;

    const variables = {
      condition1: true,
      condition2: false,
      format: "json"
    };

    const processed = engine.processTemplate(template, variables);

    assertStringIncludes(processed, "This should be included.");
    assertStringIncludes(processed, "JSON format.");
    assertEquals(processed.includes("This should not be included."), false);
    assertEquals(processed.includes("Text format."), false);
  }
});

/**
 * Test: renderTemplate substitutes variables correctly
 *
 * This test verifies that the renderTemplate function correctly substitutes
 * variables in templates. It tests both simple variable substitution and
 * handling of missing variables.
 *
 * It creates a template with multiple variables and checks that each variable
 * is correctly substituted with its value. It also checks that missing variables
 * are left as is in the template.
 */
Deno.test({
  name: "TemplateEngine - renderTemplate substitutes variables correctly",
  fn() {
    const engine = new TemplateEngine(templateDir);

    const template = `
    Hello, {{name}}!

    Your age is {{age}} and your favorite color is {{color}}.

    {{missing}} should remain as is.`;

    const variables = {
      name: "John",
      age: 30,
      color: "blue"
    };

    const rendered = engine.renderTemplate(template, variables);

    assertStringIncludes(rendered, "Hello, John!");
    assertStringIncludes(rendered, "Your age is 30 and your favorite color is blue.");
    assertStringIncludes(rendered, "{{missing}} should remain as is.");
  }
});

/**
 * Test: callLLM sends prompts to LLM
 *
 * This test verifies that the callLLM function correctly sends prompts to an LLM
 * and receives a response. It tests the basic functionality of calling an LLM
 * with a system prompt and a user prompt.
 *
 * The test is designed to work even if Ollama is not running locally. It checks
 * the structure of the response and handles both success and error cases.
 *
 * Note: This test requires Ollama to be running locally for full testing.
 */
Deno.test({
  name: "TemplateEngine - callLLM sends prompts to LLM",
  async fn() {
    const engine = new TemplateEngine(templateDir);

    const systemPrompt = "You are a helpful assistant.";
    const userPrompt = "Say hello in a friendly way.";

    const result = await engine.callLLM(systemPrompt, userPrompt);

    // We don't know if Ollama is running, so we just check the structure
    if (result.success) {
      assertEquals(result.success, true);
      assertExists(result.content);
      assertEquals(typeof result.content, "string");
      assertEquals(result.content.length > 0, true);
      assertEquals(result.error, undefined);

      console.log("LLM response:", result.content?.substring(0, 100) + "...");
    } else {
      assertEquals(result.success, false);
      assertExists(result.error);
      assertEquals(result.content, undefined);

      console.log("LLM call failed:", result.error);
    }
  },
  sanitizeResources: false,
  sanitizeOps: false,
});
