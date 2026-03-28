# simon-willison-s-weblog

*Generated: 2026-03-28T21:10:16.298324+00:00 | 30 articles*

---

## Profiling Hacker News users based on their comments

*Source: https://simonwillison.net/2026/Mar/21/profiling-hacker-news-users/#atom-everything*
*220 words | Summarized in 5.7s*

Here are 2-3 concise paragraphs summarizing the article:

Simon Willison has been experimenting with a tool that fetches comments from the Hacker News API for any user, which he then uses to generate a profile of that user. The tool, built using Algolia's API and Claude Opus 4.6, produces surprisingly accurate profiles by analyzing the user's comments. For example, Willison used the tool to generate a profile of himself, which included details about his professional identity as an independent developer, his views on AI coding tools, and his interests outside of work.

The tool's effectiveness is attributed to the open CORS headers of Algolia's API, allowing JavaScript code to access the API from any web page. Willison has also tweaked the tool with Claude, which enables him to generate profiles for other users. The tool's accuracy relies on the user's willingness to share publicly available information about themselves.

The implications of this technology are multifaceted. On one hand, it highlights the ease with which large amounts of personal data can be collected and analyzed. On the other hand, it demonstrates the potential for AI-powered tools to generate insightful profiles of individuals based on their online behavior. Willison's project raises questions about the responsible use of such tools and the need for transparency and moderation in online spaces like Hacker News.

---

## Turbo Pascal 3.02A, deconstructed

*Source: https://simonwillison.net/2026/Mar/20/turbo-pascal/#atom-everything*
*183 words | Summarized in 4.4s*

Here are 2-3 concise paragraphs summarizing the article:

Simon Willison's project involved deconstructing Turbo Pascal 3.02A, a 1985 executable file that included a full text editor and Pascal compiler. He used Claude, an AI model, to decompile the binary and create an interactive artifact illustrating the result. However, upon reviewing the annotations, it was discovered that the annotated disassembly contained "hallucinated slop," meaning fabricated code with plausible-sounding labels and comments.

Further investigation revealed that the suspicious code included instructions that couldn't possibly work, such as a system call dispatcher instruction that would misalign the stack. A commenter on Hacker News, who understands assembler, reviewed the annotations and confirmed that they were indeed "slop." The AI model Claude was also re-run with updated instructions to re-review their code, which agreed with the assessment.

The project highlights the limitations of current AI models in decompiling and analyzing binary files. While these models can generate convincing results, they often rely on fabrication or incomplete analysis. This experience serves as a reminder that manual verification and human review are still essential when working with complex software artifacts.

---

## Auto mode for Claude Code

*Source: https://simonwillison.net/2026/Mar/24/auto-mode-for-claude-code/#atom-everything*
*182 words | Summarized in 4.3s*

Here is a summary of the article in 2-3 concise paragraphs:

Claude Code has introduced "auto mode", a new permissions mode that automates permission decisions for users. The mode uses a classifier model to review conversations and decide whether an action matches the user's intent, blocking actions that escalate beyond the task scope or appear to be driven by hostile content.

The auto mode allows certain operations, such as installing packages from declared dependencies in requirements files, reading-only API calls, and GET requests, while blocking other actions like force pushing on Git, downloading and executing code from external sources, and deleting files on cloud storage. The classifier model runs on Claude Sonnet 4.6, even if the main session uses a different model.

The auto mode includes an extensive set of default filters, which can be customized further with user rules. However, Simon Willison expresses concerns about the effectiveness of prompt injection protections that rely on AI, citing non-deterministic nature and potential for errors. He advocates for a more robust sandbox approach to restrict file access and network connections in a deterministic way.

---

## Vibe coding SwiftUI apps is a lot of fun

*Source: https://simonwillison.net/2026/Mar/27/vibe-coding-swiftui/#atom-everything*
*182 words | Summarized in 5.4s*

Here are 2-3 concise paragraphs summarizing the article:

Simon Willison has built two SwiftUI apps, Bandwidther and Gpuer, using Vibe coding, a technique that allows him to create macOS apps without opening Xcode. Bandwidther monitors network bandwidth usage, while Gpuer shows information about GPU usage. Both apps were built in a single text file and use system commands to gather data.

The apps were created with minimal prompting from Claude Opus 4.6 and GPT-5.4, which are competent at coding SwiftUI. Willison learned that a full SwiftUI app can fit in a single text file, making it easy to spin up an application without opening Xcode. He also discovered that wrapping terminal commands in a neat UI with Swift is easily achieved.

Despite their functionality, Willison notes that the apps should not be trusted without evaluation from someone with experience in macOS internals. However, he did learn useful things from these projects, including how a single file of code can get a lot done and how to turn an app into a menu bar icon with just a few lines of extra code.

---

## Thoughts on slowing the fuck down

*Source: https://simonwillison.net/2026/Mar/25/thoughts-on-slowing-the-fuck-down/#atom-everything*
*177 words | Summarized in 3.6s*

Here are 3 concise paragraphs summarizing the article:

Simon Willison shares an article from Mario Zechner, a creator of the Pi agent framework used by OpenClaw. Zechner argues that the current trend in agentic engineering has led to a loss of discipline and agency, with developers prioritizing speed over quality. He suggests that agents can accumulate mistakes much faster than humans, leading to unsustainable codebases.

Zechner recommends slowing down development to allow for more thoroughness and consideration of the project's goals. This includes setting limits on code generation per day, reviewing code regularly, and writing key system components by hand. While Zechner is not convinced that writing by hand is the best solution, he emphasizes the need for discipline to find a balance between speed and mental thoroughness.

The article highlights the implications of relying on agents to generate code without human oversight. Agents can introduce complex issues quickly, making it difficult for developers to understand what's going on with their codebase. Zechner's recommendations aim to mitigate this problem by introducing more intentional and deliberate development practices.

---

## Using Git with coding agents

*Source: https://simonwillison.net/guides/agentic-engineering-patterns/using-git-with-coding-agents/#atom-everything*
*169 words | Summarized in 4.9s*

Here are 2-3 concise paragraphs summarizing the article:

Using Git with coding agents is a key tool for working with coding agents. Coding agents are fluent in using Git's features, allowing developers to take advantage of the full suite of Git's abilities. The basic fluency includes understanding how to create and manage commits, branches, and repositories.

Coding agents can also navigate complex merge conflicts, ensuring that code changes pass automated tests before finalizing merges. They can also search for lost code by using Git's reflog mechanism. Additionally, coding agents can handle the boilerplate required for Git bisect, a powerful debugging tool that identifies the earliest commit where a bug first appeared.

The article highlights advanced features of Git, such as rewriting history and undoing or rewriting commits. Coding agents are skilled at using these features to maintain a clean and efficient repository history. The article concludes by emphasizing how coding agents can simplify complex Git operations, allowing developers to focus on writing better code rather than navigating Git complexities.

---

## Experimenting with Starlette 1.0 with Claude skills

*Source: https://simonwillison.net/2026/Mar/22/starlette/#atom-everything*
*165 words | Summarized in 5.1s*

Here are 2-3 concise paragraphs summarizing the article:

Starlette 1.0 has been released, and it includes breaking changes compared to the previous version. The main change is a new system for handling code execution on startup and shutdown, which uses an async context manager. To address potential compatibility issues with models trained on older Starlette versions, the author experimented with using Claude skills to generate code that works with 1.0.

The author created a skill document using Claude's Skill Creator feature, which cloned the new Starlette repository and generated a thorough documentation of its features. They then built a task management demo app using Starlette 1.0, which included projects, tasks, comments, and labels, and tested it manually to ensure its functionality.

The experiment demonstrates how Claude skills can be used to generate working code for specific frameworks, such as Starlette. The author's research repository contains the resulting app, which showcases the capabilities of Starlette 1.0 and the potential of AI-assisted programming with tools like Claude.

---

## Quoting David Abram

*Source: https://simonwillison.net/2026/Mar/23/david-abram/#atom-everything*
*163 words | Summarized in 3.0s*

Here is a summary of the article in 2-3 concise paragraphs:

Simon Willison shared a quote from David Abram, who emphasizes that Large Language Models (LLMs) cannot solve the hardest parts of software development, such as understanding systems, debugging, designing architectures, and making decisions. According to Abram, LLMs can only provide suggestions, act as a sounding board, or help with boilerplate code.

Abram highlights that the value in software development lies not in the use of tools like LLMs, but rather in the human decision-making process. He notes that the "real work" of software development is knowing what should exist in a system and why, which requires a level of context and understanding that LLMs cannot provide.

The quote suggests that while LLMs have made significant advancements in AI-assisted programming, they do not replace the need for human judgment and expertise in software development. Instead, developers must continue to use their skills and experience to make decisions and create value in their work.

---

## Quantization from the ground up

*Source: https://simonwillison.net/2026/Mar/26/quantization-from-the-ground-up/#atom-everything*
*155 words | Summarized in 3.3s*

Here are 3 concise paragraphs summarizing the article:

Quantization of Large Language Models (LLMs) involves reducing the precision of floating-point numbers to binary digits. This process is crucial for efficient deployment and inference of LLMs in resource-constrained devices or environments. However, quantization can also introduce outliers that exist outside of the normal tiny-value distribution.

These outliers are rare but extremely important to model quality, as removing even a single "super weight" can cause the model to output complete gibberish. Real-world quantization schemes often preserve these outliers by not quantizing them at all or saving their location and value into a separate table before removing them.

The article discusses the impact of quantization on model accuracy using concepts such as perplexity and KL divergence. The author found that 16-bit to 8-bit quantization carries almost no quality penalty, while 16-bit to 4-bit quantization is more noticeable but still retains around 90% accuracy compared to the original model.

---

## Malicious litellm_init.pth in litellm 1.82.8 — credential stealer

*Source: https://simonwillison.net/2026/Mar/24/malicious-litellm/#atom-everything*
*153 words | Summarized in 3.5s*

Here is a summary of the article in 2-3 concise paragraphs:

A malicious package, litellm v1.82.8, was published to PyPI and compromised with a credential stealer hidden in a base64-encoded file called litellm_init.pth. This allowed the package to be installed without running any code, triggering the credential stealer to steal sensitive information such as SSH keys, Git credentials, AWS access keys, and others.

The compromise is believed to have started with a recent exploit against Trivy, a security scanner tool used in CI by LiteLLM. Stolen PyPI credentials were then used to directly publish the vulnerable package. The affected version of litellm was quarantined by PyPI shortly after the issue was discovered.

The credential stealer stolen sensitive information from various directories and files, including personal authentication tokens and configuration files. If an individual had installed the compromised litellm package, they would have been exposed to this malicious activity without being aware of it.

---

## PCGamer Article Performance Audit

*Source: https://simonwillison.net/2026/Mar/22/pcgamer-audit/#atom-everything*
*150 words | Summarized in 2.9s*

Here are 3 concise paragraphs summarizing the article:

A performance audit of a PCGamer article revealed severe page bloat, with over 82% of network traffic and transferred bytes attributed to ad-tech, tracking, and programmatic advertising scripts. The core content consists of only 10-15 KB of text and a handful of images, yet triggers over 431 network requests and 5.5 MB of transfer within 60 seconds.

The page's poor performance is exacerbated by autoplay video carousels, which increase the load to over 200 MB in Firefox. This highlights the issue of web bloat, where excessive content and scripts can significantly impact page loading times.

The audit was conducted by Rodney, who used Claude Code for web use, and was inspired by a previous article that recommended RSS readers with significant page bloat. The findings have implications for website performance and user experience, emphasizing the need for efficient and streamlined content delivery.

---

## datasette-llm 0.1a1

*Source: https://simonwillison.net/2026/Mar/25/datasette-llm/#atom-everything*
*149 words | Summarized in 3.2s*

Here is a summary of the article in 2-3 concise paragraphs:

The datasette-llm plugin, version 0.1a1, has been released. This plugin integrates Large Language Models (LLMs) into Datasette plugins such as datasette-enrichments-llm. The new release introduces two main features: a `register_llm_purposes()` hook and a `get_purposes()` function for retrieving registered purpose strings.

These changes allow plugins to configure which models are used for specific purposes, enabling more flexible and customizable data enrichment. For example, a plugin can use `model = await llm.model(purpose="enrichment")` to specify the model to be used for a particular task. The new hook also enables future plugins to list registered purpose strings in one place.

The implications of this release are that it expands the capabilities of Datasette plugins and provides more flexibility for data enrichment tasks. It also enables plugins to register their purposes and models in a centralized manner, which can simplify maintenance and updates.

---

## LiteLLM Hack: Were You One of the 47,000?

*Source: https://simonwillison.net/2026/Mar/25/litellm-hack/#atom-everything*
*147 words | Summarized in 3.0s*

Here is a summary of the article in 2-3 concise paragraphs:

A security exploit was discovered in LiteLLM, which was released on PyPI. The exploit allowed for arbitrary code execution, and it was found that 46,996 packages were downloaded during a 46-minute period they were live on PyPI. This number includes both compromised release versions (1.82.7 and 1.82.8) and dependent packages.

An investigation by Daniel Hnyk used the BigQuery PyPI dataset to determine the extent of the exploit. It was found that 2,337 packages depended on LiteLLM, with 88% of these packages not pinning versions in a way that would have avoided the exploited version.

The implications of this exploit are significant, as it highlights the vulnerability of the Python package ecosystem. The incident is also notable for its speed, as the exploit was discovered and identified within just a few hours of being released on PyPI.

---

## My minute-by-minute response to the LiteLLM malware attack

*Source: https://simonwillison.net/2026/Mar/26/response-to-the-litellm-malware-attack/#atom-everything*
*143 words | Summarized in 3.6s*

Here is a summary of the article in 2-3 concise paragraphs:

Callum McMahon reported a malware attack on PyPI, indicating that the LiteLLM library version 1.82.8 had malicious code. The malware was found to be live on PyPI as of March 26, 2026, and anyone installing or upgrading the litellm library would be infected.

Simon Willison, the author of the blog post, provides minute-by-minute details of his response to the attack. He used a tool called Claude to analyze the malicious code and confirmed that it was indeed present in the litellm==1.82.8 package. The malicious code imports base64-b64decode('aW1wb3J0IHN1YnByb2Nlc3MKaW1wb3J0IHRlbXBmaWxl...').

The implications of this attack are significant, as it highlights the vulnerability of PyPI and the potential risks of using compromised packages in software development. The article concludes with a call to action for users to report security issues to PyPI's security contact address immediately.

---

## Package Managers Need to Cool Down

*Source: https://simonwillison.net/2026/Mar/24/package-managers-need-to-cool-down/#atom-everything*
*143 words | Summarized in 3.6s*

Here are 3 concise paragraphs summarizing the article:

Package managers have implemented various cooldown mechanisms to prevent malicious dependencies from being installed. These mechanisms, such as minimumReleaseAge and npmMinimalAgeGate, delay the installation of updated dependencies for a few days after they are released.

Recent major package managers have introduced or improved these cooldown mechanisms: pnpm (minimumReleaseAge), Yarn (npmMinimalAgeGate), Bun (minimumReleaseAge via bunfig.toml), Deno (--minimum-dependency-age), uv (added relative duration support and per-package overrides), pip (--uploaded-prior-to), and npm (min-release-age). However, pip currently only supports absolute timestamps.

Seth Larson has found a workaround for pip's limitation by using a scheduled cron to update the absolute date in the pip.conf config file. This allows pip to support relative dates as well. The article highlights the need for package managers to cool down and implement robust cooldown mechanisms to prevent supply chain attacks like the recent LiteLLM attack.

---

## Streaming experts

*Source: https://simonwillison.net/2026/Mar/24/streaming-experts/#atom-everything*
*141 words | Summarized in 3.1s*

Here are 2-3 concise paragraphs summarizing the article:

Dan Woods and others have continued to experiment with streaming experts, a technique that allows larger models to run on hardware with limited RAM by streaming necessary weights from SSD. Recently, @seikixtc ran a colossal model (Kimi K2.5) in 96GB of RAM on an M2 Max MacBook Pro, while @anemll successfully ran the same model on an iPhone.

Dan Isaac has also made progress, getting Kimi K2.5 to run on a 128GB M4 Max at around 1.7 tokens/second. These experiments aim to find optimizations for models like Qwen3.5-397B-A17B, which can be challenging to run due to their large size.

The implications of these experiments are that streaming experts may become a viable technique for running large models on hardware with limited resources, potentially making them more accessible to a wider range of users.

---

## JavaScript Sandboxing Research

*Source: https://simonwillison.net/2026/Mar/22/javascript-sandboxing-research/#atom-everything*
*136 words | Summarized in 2.9s*

Here is a summary of the article in 2-3 concise paragraphs:

Simon Willison's blog post discusses a research study on JavaScript sandboxing, which aims to compare core approaches and prominent npm packages for running untrusted code. The research focuses on Node.js (including worker_threads, node:vm, and the Permission Model), as well as alternative engines like quickjs-emscripten.

The study analyzes six different sandboxing options: isolated-vm, vm2, quickjs-emscripten, QuickJS-NG, ShadowRealm, and Deno Workers. The research aims to provide a comprehensive comparison of these approaches, including their strengths, weaknesses, and implications for security and performance.

The study is part of Simon Willison's ongoing research on JavaScript sandboxing, which was inspired by his previous work on Node.js worker threads. The findings of this study will likely be useful for developers looking to improve the security and isolation of their JavaScript applications.

---

## datasette-files 0.1a2

*Source: https://simonwillison.net/2026/Mar/23/datasette-files/#atom-everything*
*133 words | Summarized in 2.7s*

Here is a summary of the article in 2-3 concise paragraphs:

The latest release of `datasette-files` version 0.1a2 adds several new features to the plugin, which allows users to upload files directly into a Datasette instance. The changes include the use of a new column_types system, a file_actions plugin hook, and an ability to import uploaded CSV/TSV files to a table.

The release also includes improvements to the UI, including the ability to upload multiple files at once via the new documented JSON upload API. Additionally, thumbnails are now generated for image files and stored in an internal datasette_files_thumbnails table.

This update is part of the Datasette project, which is a Python-based web application framework for displaying data in various formats. The release notes can be found on the GitHub repository for `datasette-files`.

---

## Starlette 1.0 skill

*Source: https://simonwillison.net/2026/Mar/23/starlette-1-skill/#atom-everything*
*124 words | Summarized in 2.4s*

Here is a summary of the article in 2-3 concise paragraphs:

The Starlette 1.0 skill offers a guide for building robust web applications with Starlette, a lightweight ASGI framework. The accompanying demo showcases a task management app that demonstrates Starlette's flexibility in handling routing, templating (Jinja2), async database operations (aiosqlite), and real-time updates.

The skill is available online and can be found on the author's blog. It provides a concise guide for developers to build web applications with Starlette, making it easier for them to get started with the framework.

There are also links provided in the article, including a GitHub repository and a sponsored post, which offers a curated email digest of the month's most important LLM developments for a monthly subscription fee.

---

## We Rewrote JSONata with AI in a Day, Saved $500K/Year

*Source: https://simonwillison.net/2026/Mar/27/vine-porting-jsonata/#atom-everything*
*122 words | Summarized in 2.5s*

Here is a summary of the article in 2-3 concise paragraphs:

The Reco team rewrote JSONata, a JSON expression language, using AI in just one day. The new implementation was built on top of an existing Go version that was developed in 7 hours and $400 worth of token spend, thanks to JSONata's comprehensive test suite.

To verify the new implementation's behavior, the Reco team deployed it alongside the original code for a week, running both versions in parallel. This ensured that the new implementation matched the behavior of the old one exactly.

The rewritten JSONata implementation is expected to save the Reco team $500,000 per year, highlighting the potential benefits of using AI-generated code and vibe porting for optimizing existing projects.

---

## Quoting Matt Webb

*Source: https://simonwillison.net/2026/Mar/28/matt-webb/#atom-everything*
*119 words | Summarized in 2.4s*

Here is a summary of the article in 2-3 concise paragraphs:

Matt Webb emphasizes the importance of agentic coding, where AI agents solve problems quickly and efficiently. However, he also notes that current implementations often result in "burning a trillion tokens" to re-write code from scratch.

To address this issue, Webb advocates for great libraries that encapsulate hard problems with easy-to-use interfaces, allowing developers to build maintainable and adaptable apps. He mentions architecture as a key area of focus, implying that it should be prioritized over coding itself.

Webb's statement suggests that architecture plays a crucial role in AI-assisted programming, enabling developers to create better software by thinking about the overall system rather than just individual lines of code.

---

## Beats now have notes

*Source: https://simonwillison.net/2026/Mar/23/beats-now-have-notes/#atom-everything*
*117 words | Summarized in 2.4s*

Here are 2-3 concise paragraphs summarizing the article:

Simon Willison has updated his blog to include notes for "beats" - frequently posted content pulled in from external sources. The notes provide explanation and context, making the beats more informative. This feature was added on March 23, 2026.

The update also includes notes attached to beats in an Atom feed, allowing them to be displayed alongside regular posts. Additionally, Willison has updated his Atom feed (/atom/everything/) to include any beats with attached notes.

This change aims to improve the user experience by providing more context and explanation for frequently posted content. The updates reflect Willison's efforts to enhance his blog's functionality and provide more value to his readers.

---

## Merge State Visualizer

*Source: https://simonwillison.net/2026/Mar/22/manyana/#atom-everything*
*117 words | Summarized in 2.4s*

Here is a summary of the article in 2-3 concise paragraphs:

Simon Willison has posted about a tool called Merge State Visualizer, which was inspired by Bram Cohen's coherent vision for the future of version control using Conflict-Resolving Data Types (CRDTs). The tool is an interactive UI that visualizes how the algorithms work.

The visualizer was created from 470 lines of Python code by Bram Cohen and was explained through Simon Willison's blog. The tool uses Pyodide to build an interactive interface, allowing users to see how the algorithms work.

No specific decisions or implications are mentioned in the article, but it appears that the goal is to provide a better understanding of CRDTs and their applications.

---

## Quoting Neurotica

*Source: https://simonwillison.net/2026/Mar/23/neurotica/#atom-everything*
*113 words | Summarized in 2.1s*

Here is a summary of the article in 2-3 concise paragraphs:

Neurotica, an individual, shared a quote on March 23, 2026, expressing their opinion on "slop" - content that requires more human effort to consume than it took to produce. They believe that when someone shares raw output without editing or refinement, they are disrespecting the value of others' time.

The quote was collected by Simon Willison and posted on his blog. The article does not provide further context about Neurotica's identity or background.

The implication of the quote is that there is a need for consideration and respect for others' effort when sharing content, particularly in a professional setting such as coworking.

---

## datasette-files-s3 0.1a1

*Source: https://simonwillison.net/2026/Mar/25/datasette-files-s3/#atom-everything*
*112 words | Summarized in 2.3s*

Here are 2-3 concise paragraphs summarizing the article:

The datasette-files-s3 0.1a1 release adds a mechanism to fetch S3 configuration periodically from a URL, allowing for time-limited IAM credentials restricted to a prefix within a bucket. This enables secure storage and retrieval of files using an S3 bucket.

This update provides a backend solution for datasette-files that integrates with Amazon S3. The release is the latest iteration in the development of datasette-files-s3, which is part of the datasette project.

The implications of this release are not explicitly stated in the article, but it suggests that users can now store and retrieve files securely using an S3 bucket as a backend solution for datasette-files.

---

## Quoting Christopher Mims

*Source: https://simonwillison.net/2026/Mar/24/christopher-mims/#atom-everything*
*110 words | Summarized in 2.0s*

Here is a summary of the article in 2-3 concise paragraphs:

Quotation by Christopher Mims:
Christopher Mims, a Technology columnist at The Wall Street Journal, has expressed skepticism about giving AI total control over one's computer and entire life. He anticipates that this idea will be viewed as foolish in retrospect.

No further information is provided about the context or implications of Mims' statement, but it suggests that he may have concerns about the potential risks or unintended consequences of relying on AI for all aspects of life.

The article does not provide any additional details beyond Mims' quote and a brief mention of his background as a Technology columnist.

---

## Quoting Richard Fontana

*Source: https://simonwillison.net/2026/Mar/27/richard-fontana/#atom-everything*
*104 words | Summarized in 2.2s*

Here are 3 concise paragraphs summarizing the article:

Richard Fontana, a co-author of the LGPLv3 license, has expressed doubts about the necessity of releasing chardet 7.0.0 under the LGPL due to lack of evidence showing persistence of copyrightable expressive material from earlier versions or any other viable alternate theory of license violation.

Fontana's statement was in response to comments on the chardet relicensing situation, where he questioned whether the release of version 7.0.0 would constitute a license violation.

The implications of this decision are not explicitly stated in the article, but it suggests that the licensing requirements for chardet may be reevaluated or clarified.

---

## Quoting Kimi.ai @Kimi_Moonshot

*Source: https://simonwillison.net/2026/Mar/20/cursor-on-kimi/#atom-everything*
*91 words | Summarized in 2.1s*

Here is a summary of the article in 2-3 concise paragraphs:

Cursor AI has launched Composer 2, which was built on top of Kimi K2.5. Kimi.ai confirmed that their model provided the foundation for Cursor's system.

The launch of Composer 2 marks an integration between Kimi and Cursor, with Cursor accessing Kimi via FireworksAI_HQ hosted RL and inference platform as part of an authorized commercial partnership.

This development is seen as a key point in the open model ecosystem, with Kimi.ai expressing support for Cursor's continued pretraining and high-compute RL training.

---

## DNS Lookup

*Source: https://simonwillison.net/2026/Mar/22/dns/#atom-everything*
*89 words | Summarized in 2.1s*

Here is a summary of the article in 2-3 concise paragraphs:

Simon Willison discovered that Cloudflare's 1.1.1.1 DNS service has a CORS-enabled JSON API, allowing for running DNS queries against all three resolvers (1.1.1.1, 1.1.1.2, and 1.1.1.3). He had Claude Code build a UI for running these queries.

This development enables users to query the Cloudflare DNS services programmatically, potentially expanding their options for DNS resolution and filtering.

The discovery has implications for applications that require robust DNS capabilities, such as those dealing with security or content filtering requirements.

---

## datasette-showboat 0.1a2

*Source: https://simonwillison.net/2026/Mar/27/datasette-showboat/#atom-everything*
*78 words | Summarized in 2.0s*

Here is a summary of the article in 2-3 concise paragraphs:

Datasette Showboat 0.1a2 has been released, adding an option to export a Markdown file that allows Showboat to incrementally publish updates to a remote server.

The new feature enables users to update their Showboat publication remotely without having to re-publish the entire dataset every time. This is made possible through the addition of a `datasette-showboat` plugin.

The release notes for this version can be found at https://github.com/simonw/datasette-showboat/releases/tag/0.1a2.
