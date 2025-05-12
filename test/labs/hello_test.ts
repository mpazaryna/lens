import { assertEquals } from "@std/assert";
import { hello } from "@src/labs/hello.ts";

Deno.test("hello function", () => {
  assertEquals(hello(), "Hello, World!");
  assertEquals(hello("Deno"), "Hello, Deno!");
});
