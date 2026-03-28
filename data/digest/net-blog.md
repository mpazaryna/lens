# net-blog

*Generated: 2026-03-28T21:10:16.285288+00:00 | 10 articles*

---

## Release v1.0 of the official MCP C# SDK

*Source: https://devblogs.microsoft.com/dotnet/release-v10-of-the-official-mcp-csharp-sdk/*
*211 words | Summarized in 7.3s*

Here are the article's key points, decisions, and implications summarized in 2-3 concise paragraphs:

The Model Context Protocol (MCP) C# SDK has reached its v1.0 milestone, bringing full support for the 2025-11-25 version of the MCP Specification. The release delivers a rich set of new capabilities, including enhanced authorization server discovery, icons for tools, resources, and prompts, incremental scope consent, URL mode elicitation, and tool calling support in sampling.

The enhancements aim to improve security, usability, and flexibility in the MCP protocol. For example, incremental scope consent brings the Principle of Least Privilege to MCP authorization, allowing clients to request only the minimum access needed for each operation. URL mode elicitation enables secure out-of-band interactions between the server and end-user, bypassing the MCP host/client entirely. Tool calling support in sampling allows servers to include tools in their sampling requests, enabling more complex LLM invocations.

The implications of these changes are significant, as they enable more secure, efficient, and flexible use cases for the MCP protocol. Clients and servers must adapt to these new features and capabilities, which may require updates to existing codebases and infrastructure. The MCP community can now build on this solid foundation to develop innovative applications and services that leverage the power of machine learning and context protocols.

---

## Generative AI for Beginners .NET: Version 2 on .NET 10

*Source: https://devblogs.microsoft.com/dotnet/generative-ai-for-beginners-dotnet-version-2-on-dotnet-10/*
*195 words | Summarized in 7.6s*

Here is a summary of the article in 2-3 concise paragraphs:

Microsoft has released Version 2 of its free, open-source course "Generative AI for Beginners .NET", which covers building AI-powered .NET applications. The new version features a restructured curriculum into five focused lessons with full explanations and working samples. Each lesson builds on the previous one, covering topics such as introduction to generative AI, generative AI techniques, AI patterns and applications, agents with Microsoft Agent Framework, and responsible AI.

The course has been updated to work with .NET 10 and uses Microsoft.Extensions.AI as the primary abstraction layer. The new version also includes changes in authentication and model references, and the RAG samples have been rewritten with native SDKs. Additionally, a new Microsoft Agent Framework RC lesson has been added, covering multi-agent systems and tool use.

The course is available for free on GitHub Codespaces or local development, and users can start working through the lessons as they become available. The course is intended to provide a comprehensive introduction to building generative AI applications using .NET, and users are encouraged to join the fun by starting with the first lesson and reporting any issues or suggestions.

---

## Ten Months with Copilot Coding Agent in dotnet/runtime

*Source: https://devblogs.microsoft.com/dotnet/ten-months-with-cca-in-dotnet-runtime/*
*191 words | Summarized in 8.0s*

Here are 3 concise paragraphs summarizing the article:

The .NET team experimented with using GitHub's Copilot Coding Agent (CCA) in their dotnet/runtime repository for ten months. The experiment aimed to assess whether a cloud-based AI coding agent could meaningfully contribute to one of the most complex and scrutinized codebases in the world. CCA was used responsibly, with human engineers adding it to their workflow and maintaining high standards.

The results show that CCA contributed 22.2% of all Microsoft-originated pull requests by volume, with a success rate of 67.9%. However, when comparing CCA's success rate to human PRs, the differences in selection pressures and task scopes become apparent. The experiment also revealed that task scope matters more than size, with well-scoped tasks producing reliable results. Additionally, most lines added were test code, consistent with CCA's strengths.

The experiment has shown an encouraging trajectory, with the success rate climbing over time. From 41.7% in the first month to holding steady at ~71% across the most recent quarter. The data collected from seven comparison repositories provides context and contrasts, highlighting factors that influence CCA success, such as codebase age, domain complexity, and architectural patterns.

---

## Accelerating .NET MAUI Development with AI Agents

*Source: https://devblogs.microsoft.com/dotnet/accelerating-dotnet-maui-with-ai-agents/*
*186 words | Summarized in 7.2s*

Here is a summary of the article in 2-3 concise paragraphs:

The .NET MAUI team has developed a suite of specialized agents and skills that work together to streamline the contribution lifecycle. These agents, including pr-review, write-tests-agent, sandbox-agent, and learn-from-pr agent, aim to dramatically accelerate development workflow and contributor experience for the entire .NET MAUI community. The agents provide intelligent issue resolution, automated test creation, manual testing validation, and continuous improvement.

The multi-model architecture for quality assurance leverages 4 AI models sequentially in Phase 3 (Try-Fix) to provide comprehensive solution exploration. This approach ensures diverse solution exploration, comprehensive fix coverage, learning from failures, reduced hallucination, and best fix selection. The try-fix skill benefits most from this architecture, providing an independent fix proposal, empirical testing, and detailed results for comparison.

Implementing these agents has observed significant improvements across the team, including a 50-70% time reduction per issue, measurable quality improvements (95%+ test coverage, 80% first-time fix rate), and reduced back-and-forth during code reviews. The skills ecosystem is built on reusable skills that can be composed together for different workflows, enabling a flexible and modular approach to development.

---

## Modernize .NET Anywhere with GitHub Copilot

*Source: https://devblogs.microsoft.com/dotnet/modernize-dotnet-anywhere-with-ghcp/*
*185 words | Summarized in 7.7s*

Here is a summary of the article in 3 concise paragraphs:

The .NET 10 release includes modernization for .NET applications with GitHub Copilot, allowing teams to upgrade their codebases more efficiently. The new "modernize-dotnet" agent enables teams to assess, plan, and execute upgrades without leaving their preferred development environment (e.g., Visual Studio, VS Code, or terminal).

The modernization workflow generates three explicit artifacts: an assessment report, a proposed upgrade plan, and a set of upgrade tasks that apply code transformations. These artifacts live alongside the codebase, making it easier for teams to review, discuss, and modify them before execution begins. The agent supports custom skills, which allow organizations to encode internal frameworks or migration patterns into the modernization workflow.

The modernize-dotnet agent is now available in various environments, including Visual Studio, VS Code, GitHub Copilot CLI, and directly within a repository on GitHub. Migration from .NET Framework to modern .NET is supported for certain application types, with plans to support Web Forms projects in the future. The agent provides a collaborative proposal for modernization, shifting the focus from local exercises to collaborative discussions and executions.

---

## RT.Assistant: A Multi-Agent Voice Bot Using .NET and OpenAI

*Source: https://devblogs.microsoft.com/dotnet/rt-assistant-a-realtime-multiagent-voice-bot-using-dotnet-and-open-ai-api/*
*184 words | Summarized in 7.4s*

Here are 3 concise paragraphs summarizing the article:

RT.Assistant is a voice-enabled, multi-agent assistant built entirely in .NET that uses OpenAI Realtime API for low-latency, bidirectional voice. The application consists of four specialized agents: Voice Agent, CodeGen Agent, Query Agent, and App Agent, which communicate over a strongly-typed async bus hosted by the RTFlow framework.

RTAssistant's technologies showcase the integration of .NET MAUI for cross-platform native UI on iOS, Android, macOS, and Windows; F# libraries for discriminated unions and async state machines; Microsoft.Extensions.AI for portable LLM integration with OpenAI and Anthropic models; and a custom RTFlow framework that hosts multiple agents. The application uses Prolog to execute user queries against a logic-programming knowledge base embedded in a .NET MAUI HybridWebView.

The article highlights the integration of various frameworks and technologies, including RTOpenAI for real-time voice applications on WebRTC, Fabulous .NET MAUI Controls for building cross-platform native apps in F#, and Microsoft.Extensions.AI for portable LLM integration. The application aims to address a common customer pain point in the telecom industry by providing a conversational AI assistant that can make precise, verifiable answers about phone plans.

---

## Extend your coding agent with .NET Skills

*Source: https://devblogs.microsoft.com/dotnet/extend-your-coding-agent-with-dotnet-skills/*
*172 words | Summarized in 6.9s*

Here are 2-3 concise paragraphs summarizing the article:

Microsoft is introducing a new repository, dotnet/skills, which hosts a set of agent skills for .NET developers. These skills are designed to improve productivity by providing context and reducing trial and error. The skills are organized into functional areas and can be discovered and installed through a plugin marketplace.

The goal of dotnet/skills is to provide practical solutions that help agents complete common .NET tasks more reliably. To evaluate the effectiveness of these skills, Microsoft runs a lightweight validator on each merged skill, scoring it against a baseline without the skill. This approach aims to ensure that only useful and well-scoped skills are shared.

The repository will continue to evolve with frequent updates and new skills. Developers are encouraged to try out the skills in their own workflows, provide feedback, and share ideas for improvement. Microsoft also plans to work with partner teams to improve discovery and installation processes, ensuring that .NET developers have access to the best possible skills to enhance their productivity.

---

## .NET and .NET Framework March 2026 servicing releases updates

*Source: https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-march-2026-servicing-updates/*
*161 words | Summarized in 9.0s*

Here is a summary of the article in 2-3 concise paragraphs:

The latest servicing release for .NET and .NET Framework, available as of March 10, 2026, includes security improvements and non-security fixes. The release addresses several CVEs (Common Vulnerabilities and Exposures), including CVE-2026-26130, which is a security feature bypass vulnerability in .NET 10.0 and earlier versions.

The servicing release includes updates for various components of the .NET ecosystem, such as ASP.NET Core, Entity Framework Core, Runtime, WPF, WinForms, and others. The update includes fixes for known issues and provides new features and improvements. Users are advised to install the latest service release to ensure they have the most up-to-date version of .NET.

There is no new security or non-security update available in this month's servicing release for .NET Framework. However, a separate out-of-band (OOB) release was made available on March 12, 2026, to address a regression in .NET 10.0.4. This OOB release includes fixes for the macOS debugger and other issues.

---

## .NET 11 Preview 2 is now available!

*Source: https://devblogs.microsoft.com/dotnet/dotnet-11-preview-2/*
*140 words | Summarized in 7.7s*

Here are the article's key points, decisions, and implications in 2-3 concise paragraphs:

The second preview release of .NET 11 is now available. This release includes improvements across various areas such as libraries, runtime, SDK, C#, F#, ASP.NET Core, Blazor, .NET MAUI, Entity Framework Core, container images, and more.

The notable improvements in this release include a 15% speedup for Matrix4x4.GetDeterminant, smaller SDK installers on Linux and macOS, and improved code analyzer capabilities. Additionally, Entity Framework Core has gained support for LINQ MaxBy, MinBy, SQL Server DiskANN vector indexes, and SQL Server full-text catalogs.

The .NET 11 Preview 2 release is now available for download, and it includes the necessary changes to get started with the new version. The release notes provide a comprehensive list of changes, including experimental CoreCLR support for .NET for iOS, Mac Catalyst, macOS, and tvOS.

---

## .NET 10.0.5 Out-of-Band Release – macOS Debugger Fix

*Source: https://devblogs.microsoft.com/dotnet/dotnet-10-0-5-oob-release-macos-debugger-fix/*
*127 words | Summarized in 7.8s*

Here is a summary of the article in 2-3 concise paragraphs:

Microsoft is releasing .NET 10.0.5 as an out-of-band (OOB) update to address a regression introduced in .NET 10.0.4, which causes the debugger to crash when debugging applications on macOS using Visual Studio Code.

The issue specifically affects macOS users, particularly those using Apple Silicon/ARM64, and is caused by a crash when attempting to debug any .NET application on macOS. The update is available for download and installation on macOS users who have installed .NET SDK 10.0.104 or 10.0.200 or .NET 10.0.4 runtime.

The update only addresses the specific crash issue and does not include additional fixes beyond what was released in .NET 10.0.4. Other platforms (Windows, Linux) and development environments are not affected by this regression.
