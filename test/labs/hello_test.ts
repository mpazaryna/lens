import { assertEquals } from "@std/assert";
import { hello } from "@labs/hello.ts";

Deno.test("hello function", () => {
  assertEquals(hello(), "Hello, World!");
  assertEquals(hello("Deno"), "Hello, Deno!");
});
