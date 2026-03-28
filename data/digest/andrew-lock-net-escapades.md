# andrew-lock-net-escapades

*Generated: 2026-03-28T21:10:16.205409+00:00 | 25 articles*

---

## Trying out the Zed editor on Windows for .NET and Markdown

*Source: https://andrewlock.net/trying-out-the-zed-editor-on-windows-for-dotnet-and-markdown/*
*223 words | Summarized in 8.3s*

Here is a summary of the article in 2-3 concise paragraphs:

The author was dissatisfied with Visual Studio Code (VS Code) due to its slow performance, annoying features, and missing functionalities. They were introduced to Zed, an editor that was created by Nathan Sobo, a developer who previously worked on Atom at GitHub. The author installed Zed and tried it out for their daily use, finding it to be fast, smooth, and snappy.

However, the author soon realized that Zed was missing some essential features, such as full support for Markdown, Razor, and cshtml files. They also found that many of the shortcuts they were used to in VS Code didn't work in Zed, requiring them to manually add custom mappings. The author also noted that Zed's AI-powered features were not something they wanted or needed, but could be disabled if desired.

In conclusion, the author won't be replacing VS Code with Zed just yet, as it was missing too many essential features for their use case. However, they do see a potential future where enough of these missing features are added that they'll consider making the switch. The author praises the care and attention to detail that has gone into building Zed, and notes that the team is shipping updates regularly, which suggests that the editor is still in development and improving.

---

## Exploring the .NET boot process via host tracing

*Source: https://andrewlock.net/exploring-the-dotnet-boot-process-via-host-tracing/*
*217 words | Summarized in 9.0s*

Here are 2-3 concise paragraphs summarizing the key points, decisions, and implications of the article:

Enabling host tracing in .NET applications requires setting an environment variable `COREHOST_TRACE=1` and optionally redirecting output to a file using `COREHOST_TRACEFILE`. The tracing feature provides detailed diagnostic information about the early steps of a .NET application's "boot" process. By enabling host tracing, developers can gain insights into why their application is using the wrong version of .NET.

The boot process involves several components, including the `dotnet` muxer, `hostfxr`, and the `.NET Host Framework Resolver`. The muxer searches for the correct runtime to load by reading the `runtimeconfig.json` file of the app. It then loads the `hostfxr` library, which parses arguments to decide what to execute (e.g., SDK commands or application execution). The tracing logs show this process in detail, providing a high-level understanding of how these components interact.

The implications of host tracing are that it can be used to debug issues with .NET applications, such as determining why a wrong version of .NET is being used. By analyzing the tracing logs, developers can identify potential problems and troubleshoot their application more effectively. Additionally, this feature provides a way to gain insights into the inner workings of the .NET runtime and its components, which can be useful for optimizing performance and reliability.

---

## Understanding the worst .NET vulnerability ever: request smuggling and CVE-2025-55315

*Source: https://andrewlock.net/understanding-the-worst-dotnet-vulnerability-request-smuggling-and-cve-2025-55315/*
*208 words | Summarized in 7.6s*

Here are 2-3 concise paragraphs summarizing the article:

The .NET CVE-2025-55315 vulnerability, also known as request smuggling, allows an authorized attacker to bypass a security feature over a network. This vulnerability is rated 9.9 out of 10 by Microsoft, their highest ever rating. Request smuggling enables sending a secret request to a destination server that an intermediate proxy server hasn't seen, which can be exploited in various ways, including stealing data from other users' requests.

Request smuggling works by exploiting differences between proxies and servers in how they parse HTTP requests. In general, it involves creating an invalid HTTP request that looks like two requests glued together, with the second request being "smuggled" past the proxy to the server. The vulnerability relies on a specific variation using Transfer-Encoding: chunked and Chunk Extensions, which allows sending data in multiple chunks without knowing the overall size of the data.

The vulnerability affects ASP.NET Core applications that read or manipulate request streams, even if they don't explicitly use a proxy server. It can be exploited to bypass authentication controls, make internal requests (SSRF), perform injection attacks, and more. To protect against this vulnerability, developers should consider any code that reads, manipulates, or forwards request streams as a potential avenue of exploitation.

---

## Converting an xUnit test project to TUnit

*Source: https://andrewlock.net/converting-an-xunit-project-to-tunit/*
*205 words | Summarized in 8.0s*

Here are 3 concise paragraphs summarizing the article:

The author discusses the new TUnit testing framework and its features, including source-generated tests, parallel execution by default, and Native AOT support. They also highlight the differences between TUnit and xUnit, including the ability to choose the number of tests to run in parallel, set up and tear down methods, assembly-level hooks, test context, and assertions.

The author decided to convert one of their open-source libraries from xUnit to TUnit due to xUnit.v3's limited support for older frameworks. They found that converting to TUnit was relatively smooth using Roslyn analyzers, which converted the project to TUnit with minimal changes on their part. The author notes that while TUnit has some features not available in xUnit, it also has its own set of differences.

The conversion process involved adding the TUnit package, removing global usings, converting xUnit usages to TUnit, reinstating global usings, and removing unneeded packages. However, the author encountered some minor issues, including fixing Assert calls that weren't converted correctly and working around limitations in their build system's support for the new test platform. They also noted that Verify, a snapshot testing library, is not compatible with TUnit due to its limited .NET Core version support.

---

## Using and authoring .NET tools

*Source: https://andrewlock.net/using-and-authoring-dotnet-tools/*
*204 words | Summarized in 8.5s*

Here is a summary of the article in 2-3 concise paragraphs:

When authoring .NET tools, ensuring compatibility with different customer environments can be challenging. One approach is to use multi-targeting, which involves building and packaging the tool for multiple target frameworks. However, this can increase the size of the NuGet package and has downsides. An alternative approach is to set the `RollForward` property in the project file, which allows the tool to run with a newer version of the runtime than it was built for.

The `RollForward=Major` setting enables the tool to run with any runtime that's available for .NET 6 or above, making it more future-proof. This approach is recommended as it provides robustness and support for currently unreleased .NET versions. Additionally, this setting can be used to roll forward compatibility with newer versions of .NET.

When working with .NET tools in a continuous integration (CI) environment, there are some handy options available. These include using the `--source` and `--tool-path` flags when installing local packages, which ensure that only the correct package is installed and that it's installed to the correct location. Additionally, the `--allow-downgrade` option can be used when updating a tool, which allows for downgrading to an older version if necessary.

---

## Supporting platform-specific .NET tools on old .NET SDKs: Exploring the .NET 10 preview - Part 8

*Source: https://andrewlock.net/exploring-dotnet-10-preview-features-8-supporting-platform-specific-dotnet-tools-on-old-sdks/*
*200 words | Summarized in 7.5s*

Here are 3 concise paragraphs summarizing the key points, decisions, and implications:

The introduction of platform-specific tools in .NET 10 provides benefits such as a simpler support matrix, reduced package size, and faster startup times. However, these features come with a trade-off: consumers must use the .NET 10 SDK to install and run platform-specific tools. This presents a challenge for tool authors who need to balance the benefits of platform-specific packages with the requirement that users have the latest SDK.

To mitigate this issue, tool authors can consider creating "compromise" packages that combine framework-dependent and platform-specific tools. These packages would include both the standard, non-platform-specific version of the tool and a version tailored for the .NET 10 SDK. This approach allows consumers to use the most optimized version of the package while still supporting earlier versions of the SDK.

The decision to adopt this compromise solution depends on the specific needs of the tool and its target audience. While it may not be suitable for all tools, especially those that require Native AOT compilation or have significant platform-specific dependencies, it can provide a middle ground between the benefits of platform-specific packages and the requirement that users have the latest SDK.

---

## Adding metadata to fallback endpoints in ASP.NET Core

*Source: https://andrewlock.net/adding-metadata-to-fallback-endpoints-in-aspnetcore/*
*195 words | Summarized in 7.6s*

Here are 2-3 concise paragraphs summarizing the article:

In ASP.NET Core, metadata can be added to endpoints to control functionality. This is done through various attributes and extension methods, such as [AllowAnonymous] or RequireAuthorization(). The RoutingMiddleware chooses which registered endpoint to execute for a given request at runtime, allowing subsequent middleware to inspect endpoint details and act accordingly.

Fallback routing in ASP.NET Core allows routes to match any incoming request that doesn't match another route. Adding metadata to fallback endpoints can control their behavior. However, when using Razor Pages or MVC, adding metadata to the MapFallbackToPage() call does not work as expected. This is because MapFallbackToPage() registers a new endpoint with a catch-all route pattern and handler, which means that the metadata is not propagated to the underlying page.

This limitation affects how metadata behaves on fallback routes. For minimal APIs, adding metadata to MapFallback() or MapFallbackToFile() works correctly, allowing anonymous access to the fallback route. In contrast, Razor Pages and MVC require more explicit configuration, such as using the [AllowAnonymous] attribute directly on the page. This highlights the differences in routing infrastructure between ASP.NET Core's various parts, including minimal APIs, MVC, and Razor Pages.

---

## Creating a .NET CLR profiler using C# and NativeAOT with Silhouette

*Source: https://andrewlock.net/creating-a-dotnet-profiler-using-csharp-with-silhouette/*
*191 words | Summarized in 8.1s*

Here is a summary of the article in 3 concise paragraphs:

The author creates a basic .NET CLR profiler using Silhouette, a library that makes it easy to work with NativeAOT and unmanaged APIs. The profiling API is used to monitor an application's execution by the CLR. To create a profiler, the author derives from Silhouette's CorProfilerCallbackBase class and decorates it with a Profiler attribute and a unique Guid.

The Initialize method is implemented, which is called when the runtime is initialized. This method returns an HRESULT value indicating success or failure. The author uses the ThrowIfFailed approach to simplify error handling by catching Win32Exception exceptions that are thrown if the operation fails. The profiler also implements the AssemblyLoadFinished method, which is called when an assembly has finished loading.

The gains of using Silhouette and NativeAOT for building a .NET CLR profiler include ease of use, flexibility, and performance. The library handles the messy work of setting up entrypoints and exposing .NET types as C++ interfaces, allowing developers to write their logic in C#. The author demonstrates how to implement basic profiling functionality using Silhouette, including logging assemblies loaded during runtime.

---

## Passkey support for ASP.NET Core identity: Exploring the .NET 10 preview - Part 6

*Source: https://andrewlock.net/exploring-dotnet-10-preview-features-6-passkey-support-for-aspnetcore-identity/*
*191 words | Summarized in 8.0s*

Here are 2-3 concise paragraphs summarizing the key points, decisions, and implications of the article:

The .NET 10 preview 6 has added support for passkeys to ASP.NET Core Identity. Passkeys provide a secure, password-less way to authenticate with websites and apps, based on standards provided by FIDO (Fast IDentity Online). The new feature allows users to sign in to apps using biometrics or a PIN, offering an inherently more secure authentication method than passwords.

The passkey support is available in the Blazor template, which includes changes such as adding a new section for managing passkeys, updating components like Login.razor and ManageNavMenu.razor, and introducing custom elements like PasskeySubmit.razor. The backend has also been updated with new APIs and EF Core migrations to save user passkey information.

The implementation of passkey support involves interactions between the browser's WebAuthn features and ASP.NET Core Identity endpoint routes, such as /Account/PasskeyCreationOptions. Two new functions, createCredential() and requestCredential(), are used to make calls to these endpoints, which trigger the browser to create or try to login using a passkey credential. While the feature offers improved security, it may have usability challenges when sharing passkeys between multiple devices.

---

## sleep-pc: a .NET Native AOT tool to make Windows sleep after a timeout

*Source: https://andrewlock.net/sleep-pc-a-dotnet-tool-to-make-windows-sleep-after-a-timeout/*
*190 words | Summarized in 8.6s*

Here is a summary of the article in 2-3 concise paragraphs:

The author built a .NET tool called "sleep-pc" that forces a Windows PC to go to sleep after a specified timeout. The initial version used the Win32 API `SetSuspendState` to send the laptop to sleep, but it was limited by its hardcoded timing and lack of flexibility. To improve this, the author added command-line argument parsing, help generation, and validation using the ConsoleAppFramework library.

To enable Native AOT compilation, the author added the necessary settings to their project file, including `PublishAot` and `TrimmerRemoveSymbols`. This resulted in a significantly smaller binary size of around 3.3MB. The tool was also packaged as two NuGet packages, with one containing the .NET 8 framework-dependent build and another containing the platform-specific Native AOT asset.

The author improved the console output by using a trick to update the countdown timer without resorting to `Thread.Sleep` or `Task.Wait`. This involved sending backspaces in the console output to "replace" the text, creating an illusion of updating in place. The full code for the tool is available on GitHub and can be installed using `dotnet tool install -g sleep-pc`.

---

## The Windows File Explorer replacement, File Pilot, is awesome

*Source: https://andrewlock.net/windows-explorer-replacement-filepilot-is-awesome/*
*186 words | Summarized in 7.5s*

Here are 2-3 concise paragraphs summarizing the article:

File Pilot is a Windows File Explorer replacement that offers several features, including a fast and responsive interface, split-screen capabilities, hotkeys for everything, and customization options. The author of the article has been using File Pilot for two weeks and is impressed with its speed and feature set.

The author recommends trying out File Pilot while it's still in beta, as it's free to use at this stage. They note that File Pilot is not open-source and may be too expensive for some users, but overall, they believe it's worth trying due to its excellent performance and features. The article highlights the benefits of using a fast and efficient file explorer, such as improved productivity and reduced frustration.

The author also discusses some limitations and missing features in File Pilot, including the lack of PDF-preview support and the inability to replace native File Explorer windows. However, they acknowledge that these are minor complaints compared to the many positives of using File Pilot. Overall, the article suggests that File Pilot is a solid alternative to traditional Windows File Explorer.

---

## Making foreach on an IEnumerable allocation-free using reflection and dynamic methods

*Source: https://andrewlock.net/making-foreach-on-an-ienumerable-allocation-free-using-reflection-and-dynamic-methods/*
*184 words | Summarized in 8.1s*

Here is a summary of the article in 2-3 concise paragraphs:

The article discusses a technique to avoid allocation when calling `foreach` on an `IEnumerable<T>` using reflection and dynamic methods. The author uses .NET's pattern matching feature, which requires a `GetEnumerator()` method that returns an `Enumerator`-like type with a `Current` property and `MoveNext` method, similar to what is defined by the `IEnumerable<T>` interface.

The article highlights that when calling `foreach` on an `IEnumerable<T>`, the compiler allocates memory for the struct-based enumerator returned by the `GetEnumerator()` method. To avoid this allocation, the author proposes using reflection and dynamic methods to create a custom loop that explicitly uses the struct enumerator, which is allocated on the stack.

The article introduces a new class called `AllocationFreeEnumerator` that provides a way to build an allocation-free enumerator for any enumerable type. This class uses reflection to access the necessary methods and properties of the enumerable's enumerator, and generates dynamic code using `DynamicMethod` to create an invocation-free loop. The author concludes that this technique can be used to avoid allocation when calling `foreach` on enumerables in older versions of .NET.

---

## Companies complaining .NET moves too fast should just pay for post-EOL support

*Source: https://andrewlock.net/companies-using-dotnet-need-to-suck-it-up-and-pay-for-support/*
*183 words | Summarized in 7.1s*

Here are 2-3 concise paragraphs summarizing the article:

Companies that complain about .NET moving too fast might consider paying for post-EOL (end of life) support instead. Microsoft provides official support for new versions of .NET for a limited time (2 or 3 years), after which it enters maintenance mode and security vulnerabilities are only addressed. However, running an unsupported version of .NET can leave organizations vulnerable to known security issues.

Paying for post-EOL support is not uncommon in other ecosystems, such as Java, where vendors provide substantial support durations for open-source distributions. Companies like HeroDevs offer paid support options for .NET beyond its official EOL timeline. This approach allows companies to delay major version updates if it's too painful and instead pay for support for old versions.

The idea of paying for post-EOL support is appealing to organizations that don't want to perform major version updates due to the associated risks, regulatory compliance issues, or opportunity costs. By paying for support, these organizations can avoid the difficulties of updating to a new major version while still addressing security vulnerabilities and maintaining regulatory compliance.

---

## Splitting the NetEscapades.EnumGenerators packages: the road to a stable release

*Source: https://andrewlock.net/splitting-the-netescapades-enumgenerators-packages-the-road-to-a-stable-release/*
*181 words | Summarized in 7.6s*

Here are 2-3 concise paragraphs summarizing the article:

The author of the NetEscapades.EnumGenerators package has made significant changes to its structure, resulting in three separate packages: EnumGenerators, Generator, and RuntimeDependencies. This change was made to address issues with users who were experiencing errors due to incorrect usage of the package's features.

The main reason for this restructuring is that the author realized they had inadvertently broken some users by introducing new features without proper documentation or warnings. To fix this issue, the author created a separate package (RuntimeDependencies) containing dependencies that need to be referenced at runtime by generated code. The Generator package now contains only the source generator itself, and EnumGenerators serves as a metapackage for easy installation.

The change provides more flexibility to users, allowing them to choose which packages to reference depending on their specific needs. Users can reference the Generator package directly, with optional references to RuntimeDependencies, to avoid runtime dependencies. This restructuring also avoids placing downstream dependency requirements on consumers of the library, making it easier for users to use the package's features without additional dependencies.

---

## Recording metrics in-process using MeterListener: System.Diagnostics.Metrics APIs - Part 4

*Source: https://andrewlock.net/recording-metrics-in-process-using-meterlistener/*
*175 words | Summarized in 7.4s*

Here are 2-3 concise paragraphs summarizing the article:

The article demonstrates how to consume metrics in-process using MeterListener, a type from the System.Diagnostics.Metrics API. A test ASP.NET Core app is created to generate load and send requests to itself, while another instance of the same app runs with a MeterListener configured to listen for specific metrics. The listener is used to display the results of these metrics in a table using Spectre.Console.

To create the test app, a simple "hello world" ASP.NET Core app is created and tweaked to generate load by sending requests to itself. A MetricManager class is defined to encapsulate the collection and aggregation of metrics emitted by the System.Diagnostics.Metrics APIs. The public API for this class includes methods to get metrics and dispose of the listener.

The article also explains how to configure the MeterListener, including enabling instruments and triggering observable instruments to emit measurements. The OnMeasurementRecorded callbacks are invoked whenever an instrument emits a value, and these callbacks can be used to aggregate data and display results in various ways.

---

## Packaging self-contained and native AOT .NET tools for NuGet: Exploring the .NET 10 preview - Part 7

*Source: https://andrewlock.net/exploring-dotnet-10-preview-features-7-packaging-self-contained-and-native-aot-dotnet-tools-for-nuget/*
*174 words | Summarized in 7.5s*

Here are 3 concise paragraphs summarizing the key points, decisions, and implications of the article:

The .NET 10 SDK introduces support for multiple deployment models for .NET tools, including self-contained, trimmed, Native AOT-compiled, and platform-specific options. These new features allow developers to pack tools in various ways, mirroring the different ways they can publish .NET applications today.

The article demonstrates how to generate each of these package types using a sample app and explores the NuGet packages that are produced for each scenario. The results show that some package sizes are significantly smaller than others, and that certain package types offer benefits such as reduced dependencies on the consumer having the correct .NET runtime already installed on the target machine.

The implications of these new features include improved compatibility for consumers of .NET tools, reduced package size, and increased flexibility in terms of platform support. However, some caveats and bugs are also mentioned, including a current limitation that prevents the production of an "any" package that can work on any platform with native dependencies.

---

## Publishing NuGet packages from GitHub actions the easy way with Trusted Publishing

*Source: https://andrewlock.net/easily-publishing-nuget-packages-from-github-actions-with-trusted-publishing/*
*173 words | Summarized in 7.3s*

Here is a summary of the article in 3 concise paragraphs:

Trusted Publishing is an initiative that uses existing authentication standards to connect CI infrastructure with public package repositories. It allows users to publish NuGet packages from their GitHub Actions workflow without having to generate and store API keys, while benefiting from improved security.

To set up Trusted Publishing on NuGet.org, users need to configure a trust policy, which involves creating a new policy, specifying the repository details, and selecting the workflow file that will be pushing to NuGet. Once configured, the workflow can use an OpenID Connect token to exchange for a short-lived API key, which is then used to push packages to NuGet.org.

The benefits of Trusted Publishing include ease of publishing, lack of long-lived credentials, and potential future benefits such as verification marks on published packages. The setup process involves adding permissions to the GitHub Actions workflow, using the NuGet/login@v1 action to exchange an OIDC token for a NuGet API key, and pushing the package using the generated API key.

---

## Creating standard and "observable" instruments: System.Diagnostics.Metrics APIs - Part 3

*Source: https://andrewlock.net/creating-standard-and-observable-instruments/*
*171 words | Summarized in 7.8s*

Here are 2-3 concise paragraphs summarizing the article:

The System.Diagnostics.Metrics API in .NET provides various types of instruments, including counters, up-down counters, gauges, and histograms. These instruments can be used to record metrics about an application's performance and behavior.

Observable instruments are a key concept in the Metrics API. They differ from non-observable instruments in that they only emit values when observed by a consumer. Observable instruments are useful when recording continuously changing values, such as garbage collection pause time or CPU utilization. Examples of observable instruments include ObservableCounter<T>, ObservableUpDownCounter<T>, and ObservableGauge<T>. Non-observable instruments, on the other hand, record values whenever they occur, such as Counter<T> and UpDownCounter<T>.

The article also discusses the different types of instruments and how they are used in the .NET runtime. For example, the Gauge<T> instrument is used to record "non-additive" values that overwrite previous values, while the Histogram<T> instrument is used to aggregate arbitrary values using statistics. The article provides examples of each instrument type and how they are used in the ASP.NET Core framework.

---

## Recent updates to NetEscapades.EnumGenerators: [EnumMember] support, analyzers, and bug fixes

*Source: https://andrewlock.net/recent-updates-to-netescapaades-enumgenerators/*
*170 words | Summarized in 7.6s*

Here is a summary of the article in 2-3 concise paragraphs:

The NetEscapades.EnumGenerators NuGet package has received recent updates, including improvements to metadata attribute support, analyzers, and bug fixes. The package allows developers to generate fast methods for working with enums, providing a performance boost.

New features include redesigned support for additional metadata attributes such as [Display] and [Description], which can be used to customize how ToStringFast or Parse works with the library. Additionally, new analyzers have been added to warn about incorrect usage of the package, including cases where enum members are nested in generic types, duplicate case labels, and reserved word names. Bug fixes also include improvements for handling language versions, extension members, and attribute embedding.

The updates aim to improve the quality of life for users of the package, making it easier to work with enums and reducing potential issues. The changes provide a better experience for developers who want to generate fast methods for working with enums, while also improving code quality and preventing common mistakes.

---

## Creating and consuming metrics with System.Diagnostics.Metrics APIs: System.Diagnostics.Metrics APIs - Part 1

*Source: https://andrewlock.net/creating-and-consuming-metrics-with-system-diagnostics-metrics-apis/*
*169 words | Summarized in 7.5s*

Here is a summary of the article in 2-3 concise paragraphs:

The System.Diagnostics.Metrics API provides a way to create and report on metrics generated by an application, such as counters, gauges, or histograms. The API includes various types of instruments, including counter, up/down counter, gauge, and histogram, each with its own characteristics and uses.

To collect and view the metrics, users can use dotnet-counters, a .NET tool that can install and run in production. Alternatively, users can export their metrics to a variety of formats using dotnet-counters' options. The article also demonstrates how to create custom metrics by creating an instrument and meter, registering it with dependency injection, and injecting it into the app's API handler.

The System.Diagnostics.Metrics API offers several benefits, including easy interoperability with OpenTelemetry and the ability to customize instruments for better performance or data storage efficiency. By following the example in the article, users can create custom metrics, experiment with different instrument types, and integrate their application with dotnet-counters for local monitoring and export options.

---

## Exploring the (underwhelming) System.Diagnostics.Metrics source generators: System.Diagnostics.Metrics APIs - Part 2

*Source: https://andrewlock.net/creating-strongly-typed-metics-with-a-source-generator/*
*162 words | Summarized in 7.4s*

Here are 2-3 concise paragraphs summarizing the article:

The article discusses using source generators in .NET 6 for metrics tracking. The Microsoft.Extensions.Telemetry abstractions package provides a source generator that generates code for strongly-typed metering types and methods. The author updates their sample app to use this source generator, replacing manual boilerplate with generated code.

The updated code uses the `Factory` class to create a `PricingPageViewed` metric, which is then used in the `ProductMetrics` class. The generated code provides a more efficient way of recording metrics, but has some limitations, such as not providing a description for a metric and requiring a specific attribute for unit measurement.

The author concludes that the source generator does not provide significant benefits in this example, citing drawbacks such as increased complexity, limited API, and potential duplication issues. However, it does offer an alternative solution for strongly-typed tag objects, which can help prevent programming errors by making it more obvious to pass values in the correct position.

---

## Easier reflection with [UnsafeAccessorType] in .NET 10: Exploring the .NET 10 preview - Part 9

*Source: https://andrewlock.net/exploring-dotnet-10-preview-features-9-easier-reflection-with-unsafeaccessortype/*
*154 words | Summarized in 7.5s*

Here are 3 concise paragraphs summarizing the article:

In .NET 10, the [UnsafeAccessorType] attribute allows using unsafe accessor methods to access private members of types that cannot be referenced directly. This attribute solves limitations in .NET 9 where direct reference to a type was required in the method signature.

The new attribute works by specifying the expected type as a string, which can be either fully qualified or assembly qualified. This enables accessing private members of generic types and nested classes that are marked internal but cannot be referenced directly.

Using [UnsafeAccessorType] with [UnsafeAccessor], developers can now access unreferenced types such as private fields and methods on a class hierarchy, even if the type is not directly accessible at compile-time. Examples demonstrate how to use this attribute for referencing types in accessor methods, including constructors, static methods, field references, instance field references, method calls with parameter passing by reference, generic methods, and generic constraints.

---

## Fixing an old .NET Core native library loading issue on Alpine

*Source: https://andrewlock.net/fixing-an-old-dotnet-core-native-library-loading-issue-on-alpine/*
*154 words | Summarized in 8.1s*

Here is a summary of the article in 2-3 concise paragraphs:

The author encountered an issue running .NET Core 3.1 and .NET 5 on Alpine Linux 3.17, which failed to load the SQLite native library 'e_sqlite3'. The problem was traced to a fallback path in the .NET runtime that uses the wrong runtime ID for Alpine versions older than 3.13. This caused the runtime to use the x64 runtime ID instead of the required musl runtime ID.

To resolve the issue, the author set the DOTNET_RUNTIME_ID environment variable to 'linux-musl-x64', which forced the runtime to use the correct runtime ID and load the SQLite native library correctly.

The solution is a simple but important fix for developers who need to run .NET Core on Alpine Linux. The issue highlights the importance of keeping up-to-date with the latest versions of .NET and Alpine, as well as being aware of potential compatibility issues between the two.

---

## Running .NET in the browser without Blazor

*Source: https://andrewlock.net/running-dotnet-in-the-browser-without-blazor/*
*149 words | Summarized in 8.1s*

Here are 2-3 concise paragraphs summarizing the article:

The .NET Runtime for WebAssembly allows running .NET applications in a browser without using Blazor. This feature has been available since .NET 7 and can be used to build WebAssembly Browser Apps, similar to the template provided in this article. The template uses the `dotnet new` command to create a new application with the experimental WASM templates installed.

The application is built using the `wasm-brower-app` template, which includes a stopwatch application that runs on top of the .NET Runtime for WebAssembly. The code is generated by source generators, including the `[JSImport]` and `[JSExport]` attributes, which enable marshalling between the .NET (WASM) world and the JavaScript world.

Publishing the application using `dotnet publish -c Release` enables client-side fingerprinting of static assets, improving security. The template also includes additional settings to reduce the size of the published application by optimizing compilation and compression.

---

## Recent updates to NetEscapades.EnumGenerators: new APIs and System.Memory support

*Source: https://andrewlock.net/updates-to-netescapaades-enumgenerators-new-apis-and-system-memory-support/*
*138 words | Summarized in 7.6s*

Here is a summary of the article in 2-3 concise paragraphs:

NetEscapades.EnumGenerators is a source generator NuGet package that provides fast methods for working with enums. The latest release, version 1.0.0-beta19, includes several new features. One significant update is the ability to disable number parsing, which was previously enabled by default. This allows users to customize how their enum types are parsed and can be useful in certain situations.

Another new feature is support for automatically calling `ToLowerInvariant()` or `ToUpperInvariant()` on serialized enums without allocating memory. This can be useful when working with third-party APIs that require specific naming conventions for enums.

The package also now supports the `System.Memory` NuGet package, which provides polyfills for read-only span APIs. Users can define an MSBuild property `EnumGenerator_UseSystemMemory=true` to enable these APIs in projects targeting .NET Framework or .NET Standard 2.0.
