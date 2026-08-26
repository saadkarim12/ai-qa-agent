AI QA Agent | Software Quality as a Service | BRD v1.1

Contents
1. Executive Summary ............................................................................................................................................................................... 4
2. Business Context and Problem Statement ................................................................................................................................... 4
2.1 Current Problems ........................................................................................................................................................................... 4
2.2 Opportunity ....................................................................................................................................................................................... 4
3. Product Vision and Value Proposition ........................................................................................................................................... 4
4. Business Objectives ............................................................................................................................................................................... 4
5. Target Customers and Personas ...................................................................................................................................................... 5
6. Scope ............................................................................................................................................................................................................ 5
6.1 In Scope ............................................................................................................................................................................................... 5
6.2 Out of Scope for MVP ..................................................................................................................................................................... 5
7. Two Operating Models ......................................................................................................................................................................... 6
7.1 Requirements-Driven QA ............................................................................................................................................................ 6
7.2 Autonomous Discovery QA ......................................................................................................................................................... 6
7.3 Common Pipeline ............................................................................................................................................................................ 6
8. End-to-End Customer Journey .......................................................................................................................................................... 7
9. Functional Requirements .................................................................................................................................................................... 7
10. Requirements Intelligence ............................................................................................................................................................... 8
10.1 Requirement Model ..................................................................................................................................................................... 8
11. Autonomous Application Discovery ............................................................................................................................................ 8
12. AI Test Generation .............................................................................................................................................................................. 8
12.1 Test Categories .............................................................................................................................................................................. 8
12.2 Test Case Data ............................................................................................................................................................................... 9
13. Playwright Execution ......................................................................................................................................................................... 9
13.1 Execution Statuses ....................................................................................................................................................................... 9
14. AI Failure Investigation and Evidence ........................................................................................................................................ 9
15. Quality Reporting and Notifications ......................................................................................................................................... 10
15.1 Report Content ........................................................................................................................................................................... 10
15.2 Example Metrics ........................................................................................................................................................................ 10
15.3 Notifications ................................................................................................................................................................................ 10
16. Customer Portal ................................................................................................................................................................................ 10
17. Integrations ......................................................................................................................................................................................... 11
18. Non-Functional Requirements .................................................................................................................................................... 11
19. Security, Privacy and Governance ............................................................................................................................................. 11
20. Roles and Permissions .................................................................................................................................................................... 11
AI QA Agent | Software Quality as a Service | BRD v1.1

21. Data Requirements .......................................................................................................................................................................... 11
22. Business Rules ................................................................................................................................................................................... 12
23. Success Metrics and KPIs .............................................................................................................................................................. 12
24. Commercial / Service Model ........................................................................................................................................................ 12
25. MVP and Roadmap ........................................................................................................................................................................... 12
26. Risks and Mitigations ...................................................................................................................................................................... 13
27. Assumptions and Dependencies ................................................................................................................................................ 13
28. Acceptance Criteria .......................................................................................................................................................................... 13
29. Future Vision ...................................................................................................................................................................................... 14
BRD v1.1 — Scope Expansion and Product Evolution.............................................................................................................. 15
30. Revised Product Scope ................................................................................................................................................................... 15
30.1 Current Scope — AI Black Box Tester .............................................................................................................................. 15
30.2 Future Scope — 360° AI QA Engineer .............................................................................................................................. 15
31. Product Evolution Model ............................................................................................................................................................... 15
32. Black Box Testing Capability Model .......................................................................................................................................... 16
33. Future White Box Testing Capability ....................................................................................................................................... 16
34. Future AI-Assisted Issue Resolution ......................................................................................................................................... 16
35. AI Branch Governance .................................................................................................................................................................... 17
36. Scalable Multi-Client Architecture ............................................................................................................................................. 17
37. Client Variability and Adaptation .............................................................................................................................................. 17
38. Multi-Tenant Service Architecture ............................................................................................................................................ 18
39. Expanded Functional Requirements ........................................................................................................................................ 18
40. Future 360° Quality Architecture .............................................................................................................................................. 18
41. Current-to-Future Customer Journey ...................................................................................................................................... 19
42. Product Positioning Guardrails .................................................................................................................................................. 19
43. Revised MVP Definition ................................................................................................................................................................. 19
44. Future 360° Release Definition ................................................................................................................................................... 19
45. Revised Product Roadmap ............................................................................................................................................................ 20
46. Architecture Principles .................................................................................................................................................................. 20
47. Additional Acceptance Criteria for Scalability ...................................................................................................................... 20
48. Executive Summary for COO / Product Leadership ........................................................................................................... 21
AI QA Agent | Software Quality as a Service | BRD v1.1

1. Executive Summary
AI QA Agent/Engineer is a Software Quality as a Service platform that provides on-demand QA engineering
for customer applications. Customers may provide Jira user stories, acceptance criteria, user manuals and
other documentation. If formal requirements are unavailable, the agent autonomously explores the
application, identifies workflows and user journeys, infers observable functional behavior, and creates a test
model.
The service generates and prioritizes test scenarios, executes browser tests through Playwright, investigates
failures, captures evidence, produces an actionable quality report, and sends results through channels such
as email and Microsoft Teams. The service is intended to increase QA capacity, reduce repetitive testing
effort, accelerate feedback, and make software quality accessible without requiring a large QA organization.
2. Business Context and Problem Statement
2.1 Current Problems
• QA capacity does not always scale with product and release volume.
• Manual regression testing consumes significant release time.
• Automation requires substantial initial development and ongoing maintenance.
• Many organizations have incomplete or outdated requirements and test documentation.
• Small teams may have an application but no formal QA process.
• Traditional test reports often show execution results without explaining business impact or providing
sufficient evidence.
2.2 Opportunity
AI QA Engineer converts software testing into an on-demand service. A customer can provide an application
and optionally provide requirements. The platform uses the available context, explores the product where
appropriate, executes tests, investigates failures and returns a quality decision supported by evidence.
3. Product Vision and Value Proposition
Vision: Make high-quality software testing accessible as an on-demand service to every product team.
Core promise:
“Give us your application. Get confidence back.”
• Test with requirements when customers have them.
• Discover and test applications when formal requirements are missing.
• Generate test intent dynamically rather than depending only on predefined scripts.
• Use Playwright as the browser execution engine.
• Investigate failures and provide reproducible evidence.
• Deliver executive-friendly quality insight and engineering-ready findings.
4. Business Objectives
ID Objective Outcome Priority
BO-01 Launch an on-demand QA service Customers can request testing Must
AI QA Agent | Software Quality as a Service | BRD v1.1

without scaling QA headcount
BO-02 Support requirements and no- Broader customer applicability Must
requirements modes
BO-03 Reduce time to meaningful QA Faster release decisions Must
feedback
BO-04 Automate repetitive QA activity Lower operational effort Must
BO-05 Provide evidence-backed findings Higher customer trust Must
BO-06 Support recurring QA revenue Continuous QA subscriptions Should
BO-07 Integrate with customer Higher adoption and retention Should
workflows
5. Target Customers and Personas
Persona Primary Need Value
Startup / SMB Product Team Limited QA capacity On-demand QA without large headcount
Product Manager Release confidence Quality score, risk and business impact
Engineering Lead Reproducible defects Evidence, traces and reproduction steps
QA Manager Scalable regression Automation, coverage and risk-based
execution
CTO / Technology Leader Predictable quality cost Continuous quality visibility
Enterprise QA Organization Additional execution capacity AI-assisted discovery and automation at scale
6. Scope
6.1 In Scope
• Customer onboarding
• Application registration
• Optional Jira integration
• User manual/document ingestion
• Autonomous web application discovery
• Requirements/behavior model generation
• AI test generation
• Risk prioritization
• Playwright execution
• Failure investigation
• Evidence capture
• Quality score and coverage
• Customer reports
• Email and Teams notifications
• Consultation booking
• Scan history
6.2 Out of Scope for MVP
• Autonomous production code changes
• Unrestricted destructive testing
• Guaranteed detection of every defect
• Replacing human judgment for high-risk releases
• Native mobile testing unless separately delivered
• Performance/security testing unless explicitly enabled
AI QA Agent | Software Quality as a Service | BRD v1.1

7. Two Operating Models
7.1 Requirements-Driven QA
Customer provides Jira stories, acceptance criteria, user manuals/documents and the application.
1. Ingest requirements
2. Normalize and understand requirements
3. Identify workflows and business rules
4. Generate test scenarios
5. Prioritize risk
6. Explore application where needed
7. Execute with Playwright
8. Investigate failures
9. Generate report
10. Notify customer
7.2 Autonomous Discovery QA
Customer provides an application and controlled access. Formal requirements are optional.
11. Discover reachable pages and navigation
12. Identify forms, controls and workflows
13. Identify user journeys
14. Infer observable functional behavior
15. Create discovered behavior model
16. Generate tests
17. Prioritize risk
18. Execute with Playwright
19. Investigate findings
20. Generate report
21. Notify customer
7.3 Common Pipeline
Both modes converge into: Understand → Test Plan → Risk Prioritization → Execution → Investigation →
Evidence → Quality Report.
AI QA Agent | Software Quality as a Service | BRD v1.1

                                                                     Figure 1: High Level Architecture Diagram
8. End-to-End Customer Journey
| Stage     | Customer         | Platform           | Output         |
| --------- | ---------------- | ------------------ | -------------- |
| Discover  | Visits website   | Explains service   | Understanding  |
| Consult   | Books QA expert  | Calendar workflow  | Consultation   |
| Onboard   | Starts project   | Creates project    | Project        |
Connect  Adds app/Jira/docs or only app  Validates inputs  QA context
Understand  Authorizes access  Builds requirements/behavior  Test model
model
| Test     | Starts scan  | Generates/prioritizes tests  | Test plan           |
| -------- | ------------ | ---------------------------- | ------------------- |
| Execute  | Waits        | Runs Playwright              | Execution evidence  |
Investigate  Reviews findings  Analyzes failures  Validated findings
| Report  | Receives alert  | Creates report  | Quality decision  |
| ------- | --------------- | --------------- | ----------------- |
Continue  Requests next scan  Retains project history  Continuous QA
9. Functional Requirements
| ID      | Requirement        | Priority  | Acceptance  |
| ------- | ------------------ | --------- | ----------- |
| FR-001  | Create QA project  | Must      |             |
Unique project with application
details
FR-002  Provide application URL  Must  URL validated and securely stored
| FR-003  | Connect Jira  | Must  | Authorized stories/context  |
| ------- | ------------- | ----- | --------------------------- |
imported
FR-004  Upload documentation  Must  Supported document converted
to QA context
FR-005  Run application-only mode  Must  No Jira/manual required
FR-006  Explore application  Must  Reachable workflows/pages
discovered
| FR-007  | Generate test scenarios  | Must  |     |
| ------- | ------------------------ | ----- | --- |
Scenarios include objective,
expected result and risk
AI QA Agent | Software Quality as a Service | BRD v1.1

| FR-008  | Prioritize tests  | Should  |     |
| ------- | ----------------- | ------- | --- |
High-risk/high-value scenarios
prioritized
FR-009  Execute through Playwright  Must  Results and artifacts captured
| FR-010  | Investigate failures  | Must  |     |
| ------- | --------------------- | ----- | --- |
Finding includes evidence and
likely cause
FR-011  Generate quality report  Must  Score, coverage, findings and
evidence
| FR-012  | Send notifications  | Must  | Email supported; Teams  |
| ------- | ------------------- | ----- | ----------------------- |
supported
FR-013  View historical scans  Should  Past reports and run status
available
| FR-014  | Book consultation  | Must  |     |
| ------- | ------------------ | ----- | --- |
Available slots can be selected
and booked
10. Requirements Intelligence
The Requirements Intelligence layer converts available customer context into a normalized QA model.
•  Import Jira stories, descriptions and acceptance criteria within authorized scope.
•  Extract functional requirements and business rules from supported documents.
•  Identify actors, roles, preconditions, workflows, validations and expected outcomes.
•  Detect ambiguities or missing information where possible.
•  Map requirements to generated test scenarios.
•  Maintain source → requirement → test → execution → finding traceability.
10.1 Requirement Model
| Element           |     | Example                                         |     |
| ----------------- | --- | ----------------------------------------------- | --- |
| Actor             |     | Customer / Administrator                        |     |
| Workflow          |     | Login / Checkout / Password Reset               |     |
| Rule              |     | Required billing information must be validated  |     |
| Precondition      |     | User is authenticated                           |     |
| Expected Outcome  |     | Order confirmation is displayed                 |     |
| Risk              |     | Critical / High / Medium / Low                  |     |
| Source            |     | Jira / Manual / Discovered                      |     |
11. Autonomous Application Discovery
When requirements are unavailable, the agent acts as a discovery-oriented QA engineer. Observed behavior
must be distinguished from confirmed business requirements.
•
Start from permitted application entry points.
•  Discover navigation and reachable pages.
•  Identify forms, controls, tables and interactive elements.
•  Identify likely user journeys.
•  Record observable states and transitions.
•  Build a discovered behavior model.
•  Generate positive, negative, boundary and workflow tests.
•  Flag areas where expected behavior cannot be confidently inferred.
12. AI Test Generation
12.1 Test Categories
•  Positive / happy path
AI QA Agent | Software Quality as a Service | BRD v1.1

• Negative / invalid input
• Boundary / edge cases
• Required-field validation
• Role / permission scenarios
• Navigation and user journeys
• State transitions
• Regression candidates
12.2 Test Case Data
Field Purpose
Test ID Unique identifier
Source Jira / document / discovered behavior
Objective What is validated
Preconditions Required setup
Steps Executable actions
Expected Result Expected behavior
Risk Business/technical risk
Priority Execution order
Evidence Requirements Artifacts required
Status Draft / Ready / Passed / Failed / Blocked
13. Playwright Execution
• Execute supported browser workflows with Playwright.
• Capture screenshots for important states and failures.
• Capture Playwright traces for investigation.
• Capture relevant console/network information where permitted.
• Apply controlled retries for likely transient failures.
• Distinguish product defects from environment, authentication and automation errors.
• Associate execution artifacts with the relevant test and scan.
13.1 Execution Statuses
• Passed
• Failed
• Blocked
• Skipped
• Automation Error
• Environment Error
• Needs Investigation
14. AI Failure Investigation and Evidence
A failed test should become an actionable finding rather than a raw log entry.
Component Required Content
Title Concise defect statement
Severity Critical / High / Medium / Low
Business Impact Why the issue matters
Expected Expected behavior
Actual Observed behavior
Reproduction Repeatable steps
Evidence Screenshot, trace, logs and relevant artifacts
Confidence AI confidence with rationale
AI QA Agent | Software Quality as a Service | BRD v1.1

Likely Cause Potential technical/functional cause
Recommendation Suggested next action
15. Quality Reporting and Notifications
15.1 Report Content
• Executive summary
• Quality score
• Requirements/workflow coverage
• Tests generated and executed
• Pass/fail distribution
• Risk distribution
• Critical/high findings
• Evidence and reproduction details
• AI recommendations
• Next actions
15.2 Example Metrics
Metric Example
Quality Score 92 / 100
Workflow Coverage 94%
Tests Executed 418
Passed 392
Failed 26
Critical 0
High 2
Medium 7
Evidence Items 392
15.3 Notifications
• Email after scan completion.
• Microsoft Teams summary for completed scans and important findings.
• Future channels: Jira, Slack, GitHub and CI/CD webhooks.
• Notifications should summarize the report rather than duplicate it.
16. Customer Portal
Module Purpose
Dashboard Current quality status and active projects
Projects Application and project configuration
Requirements Imported and discovered requirements
Test Cases Generated test scenarios
Runs Execution history
Findings Defects and AI investigation
Evidence Screenshots, traces and logs
Reports Customer-facing reports
Integrations Jira, Teams, email and future providers
Settings Access, notifications and project settings
AI QA Agent | Software Quality as a Service | BRD v1.1

17. Integrations
Integration Purpose Priority
Jira Requirements and issue context Must
Playwright Browser execution Must
Email Customer/internal notification Must
Microsoft Teams Team alerts Must
Google Calendar / Microsoft 365 Consultation booking Should
GitHub Future development/CI integration Should
Slack Future notifications Could
CI/CD Continuous QA triggers Could
18. Non-Functional Requirements
Area Requirement
Performance Long scans run asynchronously; UI remains responsive.
Scalability Support multiple customers, projects and concurrent scans.
Reliability Recover from transient failures and expose clear job states.
Observability Log orchestration, execution and integration events.
Usability Customer workflow understandable without QA expertise.
Accessibility Target WCAG 2.1 AA for customer-facing interfaces.
Maintainability AI, orchestration, execution and reporting are modular.
Auditability Important actions and changes are traceable.
19. Security, Privacy and Governance
• Encrypt customer credentials and never expose them in frontend code.
• Use secure server-side secret management for integration credentials.
• Test only customer-authorized applications/environments.
• Default away from destructive production actions.
• Isolate tenant data and evidence.
• Apply role-based access control.
• Make evidence retention configurable.
• Clearly distinguish AI inference from verified execution evidence.
• Do not label a defect as verified without sufficient evidence.
20. Roles and Permissions
Role Key Permissions
Customer Admin Manage project, integrations, users, scans and reports
Customer Viewer View scans, findings, evidence and reports
QA Expert Review projects, findings and consultations
Platform Admin Manage tenants and platform operations
Support Support customer within approved access scope
21. Data Requirements
Entity Core Data
Customer Name, company, contact, subscription
Project Name, application URL, environment, status
Integration Provider, connection metadata, status
Requirement Source, text, actor, rules, risk, confidence
Test Case Objective, steps, expected result, source, risk
Test Run Run ID, status, timestamps, environment
Finding Severity, expected, actual, impact, evidence, confidence
AI QA Agent | Software Quality as a Service | BRD v1.1

| Evidence  |     | Screenshot, trace, logs, artifact location  |     |
| --------- | --- | ------------------------------------------- | --- |
| Report    |     | Score, coverage, findings, recommendations  |     |
Consultation  Type, customer, date/time, timezone, meeting URL, status
22. Business Rules
•  BR-01: Requirements are optional; the application can be the only functional input.
•  BR-02: Multiple sources must retain source traceability.
•  BR-03: Discovered behavior is labeled discovered/inferred, not confirmed business requirement.
•  BR-04: A test is Passed only when its expected validation completes successfully.
•  BR-05: Automation/environment failures must not automatically become product defects.
•  BR-06: Booking slots are revalidated immediately before calendar creation.
•  BR-07: Notifications must not expose credentials or secrets.
•  BR-08: Quality score methodology must be documented and versioned.
•  BR-09: AI confidence is not equivalent to execution evidence.
•  BR-10: Customer data and projects are tenant-isolated.
23. Success Metrics and KPIs
| KPI  | Definition  |     | Direction  |
| ---- | ----------- | --- | ---------- |
Time to First Quality Result  Time from project start to first useful report  Decrease
Autonomous Coverage  Relevant workflows discovered without  Increase
supplied tests
Requirement Traceability  Requirements mapped to tests and outcomes  Increase
Evidence Completeness  Findings with sufficient reproduction evidence  Increase
False Positive Rate  Findings rejected as non-defects  Decrease
Customer Time Saved  Estimated manual QA effort avoided  Increase
Scan Repeat Rate  Customers returning for additional scans  Increase
Subscription Conversion  One-time customers becoming recurring  Increase
Customer Satisfaction  Post-report/consultation rating  Increase
24. Commercial / Service Model
The intended model is service-led rather than simply a software license.
| Package  | Customer Need  |     | Offering Concept  |
| -------- | -------------- | --- | ----------------- |
QA Scan  One-time assessment  Application scan + quality report
Continuous QA  Regular release assurance  Recurring scans + alerts + trends
Enterprise QA  Complex products  Private execution + governance + integrations
QA Consultation  Strategy/assessment  30/60-minute expert consultation
Pricing should be validated through customer discovery and execution economics. Website pricing is
illustrative until commercial validation is complete.
25. MVP and Roadmap
| Capability              | MVP  | Phase 2  | Future  |
| ----------------------- | ---- | -------- | ------- |
| Application onboarding  | ✓    |          |         |
Autonomous web discovery
|                     | ✓   |     |     |
| ------------------- | --- | --- | --- |
| AI test generation  | ✓   |     |     |

| Playwright execution  | ✓   |     |     |
| --------------------- | --- | --- | --- |
Evidence capture
|                 | ✓   |     |     |
| --------------- | --- | --- | --- |
| Quality report  | ✓   |     |     |

| Email notification  | ✓   |     |     |
| ------------------- | --- | --- | --- |
Jira integration
|     | ✓   |     |     |
| --- | --- | --- | --- |
AI QA Agent | Software Quality as a Service | BRD v1.1

| Document ingestion  | ✓   |     |     |
| ------------------- | --- | --- | --- |

| Teams notification  | ✓   |     |     |
| ------------------- | --- | --- | --- |

| Consultation booking  | ✓   |     |     |
| --------------------- | --- | --- | --- |
Recurring scans
|                       |     | ✓   |     |
| --------------------- | --- | --- | --- |
| Advanced risk engine  |     | ✓   |     |

| CI/CD  |     | ✓   |     |
| ------ | --- | --- | --- |
Slack/GitHub
|     |     | ✓   |     |
| --- | --- | --- | --- |
API testing  ✓
|                      |     |     |     |
| -------------------- | --- | --- | --- |
| Performance testing  |     |     | ✓   |
Security testing
|     |     |     | ✓   |
| --- | --- | --- | --- |
Mobile testing  ✓
|     |     |     |     |
| --- | --- | --- | --- |
26. Risks and Mitigations
| Risk  | Impact  |     | Mitigation  |
| ----- | ------- | --- | ----------- |
AI misunderstanding  High  Evidence, confidence, human review and
conservative claims
False positives  High
Evidence-based investigation and failure
classification
| Dynamic UI  | High  |     | Adaptive automation, retries and recovery  |
| ----------- | ----- | --- | ------------------------------------------ |
Credential exposure  Critical  Encryption and secure secret management
High execution cost  High  Risk-based selection and usage controls
Customer distrust  High  Transparent evidence and explainable reports
Overclaiming complete testing  High
Position as broad automated quality
assessment, not guaranteed defect detection
Calendar double booking  Medium  Server-side slot revalidation and transactional
booking
27. Assumptions and Dependencies
•  Customer authorizes testing.
•  Playwright is available as execution foundation.
•  Jira access is available when selected.
•  Documents can be parsed sufficiently.
•  Email/Teams/calendar APIs are available.
•  AI quality varies by application complexity and context.
•  Some findings require human review.
•  Production deployment requires formal security, privacy, legal and retention policies.
28. Acceptance Criteria
•  Customer can start with only an application URL.
•  Customer can optionally add Jira and/or documents.
•  Agent generates a structured test plan from supplied or discovered context.
•  Supported browser scenarios execute through Playwright.
•  Failures are classified where possible as product, environment, automation or investigation-needed.
•  Important findings contain evidence and reproducible steps.
•  Customer-facing quality report is generated after a scan.
•  Email and Teams notifications can be delivered.
•  Customer can book a QA consultation through a calendar workflow.
•
Secrets are not exposed in frontend code or reports.
•  Projects and customer data are isolated.
AI QA Agent | Software Quality as a Service | BRD v1.1

• Discovered behavior is clearly distinguished from confirmed requirements.
29. Future Vision
AI QA Engineer can evolve into a broader Software Quality as a Service platform covering functional UI
testing, API testing, accessibility, performance, security, mobile testing and continuous release assurance.
The long-term intelligence layer should connect requirements, risk, execution, evidence and quality
decisions across multiple testing disciplines.
Long-term positioning:
“Your software. Our QA Engineer. Continuous confidence.”
AI QA Agent | Software Quality as a Service | BRD v1.1

BRD v1.1 — Scope Expansion and Product Evolution
This addendum refines the product scope based on the latest product direction. The current release is an AI
Black Box Tester. The architecture must nevertheless be designed as a scalable quality engineering
framework so that future releases can introduce White Box testing, code-aware diagnosis, AI-assisted
remediation and controlled code changes.
Current product = AI Black Box Tester. Future product = 360° AI QA Engineer combining Black Box +
White Box quality engineering and controlled AI remediation.
30. Revised Product Scope
30.1 Current Scope — AI Black Box Tester
The current product operates primarily from outside the application. The agent tests observable behavior
through the application interface and permitted external interfaces without requiring source-code access.
• Application URL and authorized test credentials are the primary technical inputs.
• Jira user stories, acceptance criteria and user manuals are optional context sources.
• When requirements are absent, the agent explores the application and creates a discovered behavior
model.
• Test design is based on observable behavior, supplied requirements and risk.
• Browser execution is performed through Playwright.
• Failures are investigated using available UI, browser, console, network and execution evidence.
• Customers receive quality reports, findings, evidence and recommendations.
• The current agent does not modify customer source code.
• The current agent does not merge, commit or push source-code fixes.
30.2 Future Scope — 360° AI QA Engineer
The future platform will extend from Black Box testing into White Box and code-aware quality engineering.
Subject to customer authorization, the agent will access source code, correlate observed failures with
implementation, propose or implement fixes, validate changes and push changes to a dedicated AI branch.
• Source-code repository access.
• Code-aware analysis and test-to-code traceability.
• Static and structural analysis.
• AI-assisted root-cause localization.
• AI-generated remediation suggestions.
• AI-generated code changes under explicit customer controls.
• Automatic creation of an AI branch for proposed fixes.
• Re-execution of relevant tests after a change.
• Regression validation before creating a pull/merge request.
• Human review and approval before production merge.
31. Product Evolution Model
Dimension Current — Black Box Future — 360°
Application Access UI / authorized external interfaces UI + APIs + source code + approved
environments
AI QA Agent | Software Quality as a Service | BRD v1.1

Requirements Jira / manuals / discovery Same + code/context correlation
Exploration Application behavior Application + implementation behavior
Test Generation Behavior and requirements based Behavior + code-aware risk based
Execution Playwright browser execution Playwright + broader test layers
Investigation UI/browser/network evidence Evidence + source-code analysis
Root Cause Likely cause from runtime evidence Runtime + code-level root cause
Remediation Recommendation only AI-generated fix under controls
Code Change Not supported Create AI branch and proposed change
Validation Re-run tests Re-run tests + regression + code checks
Delivery Report / notifications Report + notifications + branch / PR/MR
32. Black Box Testing Capability Model
The MVP should be positioned as an AI Black Box Tester. The agent validates what a customer can observe
and experience in the application.
Capability Description MVP
Functional UI Testing Validate user-visible workflows and expected Yes
behavior
User Journey Testing Validate end-to-end customer workflows Yes
Form Validation Required, invalid, boundary and error Yes
handling
Navigation Testing Links, menus, routing and workflow Yes
transitions
Role-Based UI Testing Validate permitted behavior for supplied roles Yes
Regression Testing Re-run selected high-value scenarios Yes
Exploratory Testing Discover unexpected states and workflow Yes
paths
Evidence Capture Screenshots, traces and runtime evidence Yes
Requirements Traceability Map supplied/discovered requirements to Yes
tests
Quality Reporting Quality score, coverage, findings and Yes
recommendations
33. Future White Box Testing Capability
White Box capability is a future phase and should not be represented as an MVP capability. It requires
controlled source-code access and additional engineering controls.
• Repository and branch discovery.
• Language/framework detection.
• Static code analysis.
• Code-path and dependency analysis.
• Mapping defects to relevant source files and functions.
• Identifying untested or high-risk code paths.
• Analyzing test coverage alongside runtime behavior.
• Generating unit/component/API tests where appropriate.
• Correlating Black Box findings with White Box implementation evidence.
34. Future AI-Assisted Issue Resolution
The future agent should progress from finding defects to assisting with remediation. Remediation must be
controlled, auditable and reversible.
22. Detect and validate issue.
23. Investigate runtime evidence.
24. Locate probable source-code area.
AI QA Agent | Software Quality as a Service | BRD v1.1

25. Explain probable root cause.
26. Generate proposed code change.
27. Create isolated AI branch.
28. Apply change only within authorized repository/environment.
29. Run targeted regression tests.
30. Run broader relevant regression suite.
31. Run lint/static/type checks where applicable.
32. Generate change summary and evidence.
33. Create pull request/merge request for human review.
34. Do not merge to protected production branches automatically unless a future governance policy
explicitly allows it.
35. AI Branch Governance
Rule Requirement
Branch Isolation AI changes are created on a dedicated AI-generated branch.
Human Approval Production merge requires authorized human review by default.
Traceability Every AI change links to the finding/test/report that triggered it.
Validation Relevant automated tests run before a PR/MR is proposed.
Rollback AI changes remain reversible through normal source-control
mechanisms.
Secrets Repository secrets are not exposed to the AI reasoning layer
unnecessarily.
Permissions Repository access follows least privilege.
Audit Prompt, proposed change, evidence and branch/PR metadata are
auditable.
36. Scalable Multi-Client Architecture
The framework must be a scalable platform rather than a one-off automation project. Different customers
may use different technologies, workflows, authentication mechanisms, UI patterns and business domains.
• Tenant-aware project architecture.
• Configurable execution profiles.
• Pluggable connectors for requirements sources.
• Pluggable authentication strategies.
• Browser/application adapters where required.
• Model-agnostic AI orchestration layer.
• Reusable Playwright execution framework.
• Client-specific policies without forking the core platform.
• Configurable risk and test-selection policies.
• Environment-specific secrets and access controls.
• Artifact isolation by customer and project.
• Horizontal execution workers for concurrent customer scans.
37. Client Variability and Adaptation
The platform should support different enterprise applications without hard-coding the architecture around
one customer. Examples of target enterprise application environments may include LanSmith, Salesforce and
custom web applications.
AI QA Agent | Software Quality as a Service | BRD v1.1

Client-specific variation should be handled through configuration, connectors, adapters and execution
profiles rather than changing the core QA engine for each customer.
| Variation  |     | Framework Response  |     |
| ---------- | --- | ------------------- | --- |
Different UI technologies  Adaptive Playwright/page interaction layer
Different authentication  Configurable authentication adapters
| Different requirements sources   |     | Connector architecture           |     |
| -------------------------------- | --- | -------------------------------- | --- |
| Different business domains       |     | Project-specific domain context  |     |
| Different environments           |     | Environment profiles             |     |
| Different test depth             |     | Risk/execution policies          |     |
| Different notification channels  |     | Notification adapters            |     |
| Different repositories           |     | Future source-control adapters   |     |
38. Multi-Tenant Service Architecture
The service should support multiple customer organizations while maintaining strict logical isolation.
| Layer  |     | Requirement  |     |
| ------ | --- | ------------ | --- |
Tenant  Each customer organization has an isolated tenant context.
Project  Projects belong to one tenant and application/environment.
Credentials  Credentials are scoped to tenant/project and stored securely.
Artifacts  Screenshots, traces, reports and logs are tenant-isolated.
Execution  Workers receive only context required for the assigned job.
AI Context  Customer data must not be unintentionally mixed across tenants.
Notifications  Reports and alerts route only to authorized recipients.
| Audit  |     | Administrative and customer actions are traceable.  |     |
| ------ | --- | --------------------------------------------------- | --- |
39. Expanded Functional Requirements
| ID      | Requirement  | Phase    | Priority  |
| ------- | ------------ | -------- | --------- |
| FR-015  |              | Current  | Must      |
Support Black Box application-
only testing
| FR-016  |     | Current  | Must  |
| ------- | --- | -------- | ----- |
Support requirements-driven
Black Box testing
| FR-017  |     | Current  | Must  |
| ------- | --- | -------- | ----- |
Create discovered behavior model
when requirements are absent
| FR-018  | Support configurable client  | Current  | Must  |
| ------- | ---------------------------- | -------- | ----- |
execution profiles
| FR-019  | Support tenant/project isolation  | Current  | Must    |
| ------- | --------------------------------- | -------- | ------- |
| FR-020  | Correlate runtime finding with    | Future   | Should  |
source code
| FR-021  | Perform White Box code analysis   | Future  | Should  |
| ------- | --------------------------------- | ------- | ------- |
| FR-022  | Generate AI remediation proposal  | Future  | Should  |
| FR-023  | Create dedicated AI branch        | Future  | Should  |
| FR-024  | Run regression after AI code      | Future  | Should  |
change
| FR-025  | Create PR/MR with evidence  | Future  | Should  |
| ------- | --------------------------- | ------- | ------- |
| FR-026  |                             | Future  | Must    |
Support human approval
workflow
| FR-027  |     | Current  | Must  |
| ------- | --- | -------- | ----- |
Support multiple enterprise
application profiles
| FR-028  |     | Current  | Must  |
| ------- | --- | -------- | ----- |
Support scalable concurrent
execution
40. Future 360° Quality Architecture
The target architecture should evolve into a layered quality engineering platform:
35. Layer 1 — Requirements Intelligence: Jira, manuals, specifications and discovered behavior.
36. Layer 2 — Black Box Intelligence: UI exploration, user journeys and observable behavior.
37. Layer 3 — Test Intelligence: scenario generation, risk scoring and test selection.
38. Layer 4 — Execution: Playwright and future API/other execution engines.
AI QA Agent | Software Quality as a Service | BRD v1.1

39. Layer 5 — Evidence: screenshots, traces, logs, network/runtime evidence and reports.
40. Layer 6 — White Box Intelligence: source-code analysis and implementation correlation.
41. Layer 7 — Remediation: AI-generated fixes and targeted code changes.
42. Layer 8 — Validation: regression, static checks and post-fix quality assessment.
43. Layer 9 — Delivery: report, notification, AI branch and PR/MR for human review.
41. Current-to-Future Customer Journey
Stage Current MVP Future 360°
Input App + optional Jira/manual App + optional Jira/manual + code
Understand Requirements / discovered behavior Requirements + behavior + code context
Plan Black Box test plan 360° test plan
Execute Playwright Playwright + future test layers
Find Runtime defects Runtime + implementation defects
Fix Recommendation AI-assisted remediation
Validate Regression test Regression + code validation
Deliver Report + alerts Report + alerts + AI branch/PR
42. Product Positioning Guardrails
• Do not market the current MVP as White Box testing.
• Do not claim current code access or automatic code fixes.
• Do not claim guaranteed complete defect detection.
• Use “AI Black Box Tester” for the current core capability.
• Use “360° AI QA Engineer” as the future product direction.
• Use “Software Quality as a Service” as the commercial/service category.
• Clearly distinguish observed evidence, AI inference and customer-confirmed requirements.
• Future autonomous code changes require explicit authorization and governance.
43. Revised MVP Definition
The MVP is an AI Black Box Tester delivered as Software Quality as a Service. The minimum commercially
meaningful experience is:
44. Customer submits an application.
45. Customer optionally connects Jira and/or uploads documentation.
46. Agent understands available context.
47. Agent autonomously explores the application where needed.
48. Agent generates risk-prioritized Black Box tests.
49. Agent executes tests using Playwright.
50. Agent investigates failures and captures evidence.
51. Agent produces a quality report.
52. Agent sends the report through email and/or Microsoft Teams.
53. Customer can schedule a QA consultation and request another scan.
44. Future 360° Release Definition
54. Customer grants repository access.
55. Agent correlates Black Box findings with source code.
56. Agent performs White Box analysis.
AI QA Agent | Software Quality as a Service | BRD v1.1

57. Agent proposes a remediation.
58. Agent creates an isolated AI branch.
59. Agent applies the authorized change.
60. Agent executes targeted and regression tests.
61. Agent reports the original issue, code change and validation evidence.
62. Agent opens a pull request/merge request for human approval.
45. Revised Product Roadmap
Phase Focus Key Deliverables
Phase 1 AI Black Box Tester Discovery, requirements intelligence, test
generation, Playwright, evidence, reports
Phase 2 Scalable SQaaS Platform Multi-tenancy, client profiles, recurring scans,
integrations, risk engine
Phase 3 White Box Intelligence Repository access, static/code analysis, code-
aware diagnosis
Phase 4 AI Remediation Fix generation, AI branch, targeted validation,
PR/MR workflow
Phase 5 360° QA Engineer Black Box + White Box + API + accessibility +
performance/security/mobile as governed
capabilities
46. Architecture Principles
• API-first orchestration.
• Event/job-based execution for long-running scans.
• Modular AI agent architecture.
• Pluggable application and integration adapters.
• Tenant isolation by design.
• Configuration over customer-specific forks.
• Evidence-first testing.
• Human-in-the-loop governance for high-impact decisions.
• Least-privilege access.
• Observable and auditable automation.
• Provider/model abstraction to reduce lock-in.
• Execution workers that scale independently from the customer portal.
47. Additional Acceptance Criteria for Scalability
• A new client application can be onboarded without changing core test orchestration logic.
• Client-specific behavior can be configured through project profiles or adapters.
• Customer data and execution artifacts remain isolated.
• Multiple scans execute concurrently without cross-project contamination.
• Long-running test jobs do not block customer portal interactions.
• Execution workers can scale independently.
• New notification or requirements providers can be added without rewriting core business logic.
• Future source-code access can be introduced without redesigning the current Black Box execution
model.
AI QA Agent | Software Quality as a Service | BRD v1.1

48. Executive Summary for COO / Product Leadership
The recommended strategy is to launch AI QA Engineer as an AI Black Box Tester delivered through a
Software Quality as a Service model. This provides an immediately understandable customer value
proposition while avoiding the complexity and governance requirements of code-changing autonomy in the
first release.
The technical architecture should simultaneously be designed for the future 360° vision. The same
intelligence, orchestration, risk, evidence and reporting layers should be extensible from Black Box testing
into White Box analysis and controlled AI remediation. In the future, the agent can receive code access,
identify the implementation behind a defect, propose and apply a fix on a dedicated AI branch, validate the
change, and submit it for human review.
The framework must remain client-agnostic and scalable so different enterprise applications—including
environments such as LanSmith, Salesforce and custom applications—can be supported through adapters,
connectors and configurable execution profiles rather than customer-specific rewrites.
AI QA Agent | Software Quality as a Service | BRD v1.1
