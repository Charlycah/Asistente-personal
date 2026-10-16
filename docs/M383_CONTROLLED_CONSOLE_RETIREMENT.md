# M383 - Controlled Console Retirement

## M383.1 - Deprecation boundary

ROBY Desktop is the only recommended interactive interface. The historical
console remains temporarily callable so its certified diagnostics, lifecycle and
shutdown contracts can be migrated without breaking the existing runtime.

Every explicit console start displays a retirement notice. No new conversational
feature may depend exclusively on the console from this milestone onward.

## Preserved maintenance commands

`--doctor` and `--setup` are maintenance operations rather than conversational
interfaces. They remain supported.

## Conditions for physical removal

The console implementation can be deleted only after:

1. current guides and normal startup no longer depend on it;
2. required diagnostics have a Desktop or read-only replacement;
3. lifecycle startup, heartbeat and shutdown remain certified elsewhere;
4. reserved-input and trace-sanitization guarantees remain covered;
5. the full suite passes after obsolete console tests are formally archived or
   replaced by equivalent boundary tests.

## M383.2 - Diagnostic migration

The certified Desktop adapter chain now exposes the existing immutable
`UnifiedBrainDiagnosticSnapshot`. `ROBYDesktopApp.diagnostics` delegates to that
same snapshot and creates no copy, persistence path or parallel observer.

Runtime health, readiness, capabilities and cognitive-core state remain under
`UnifiedRuntimeObservability`. Gmail startup, battery awareness, reminder
awareness, lifecycle startup and lifecycle shutdown already have direct Desktop
wiring.

The console's ability to reveal provider prompts is deliberately not migrated.
ROBY's personal Desktop diagnostic surface must remain metadata-only and cannot
display user messages, assistant response text or provider payloads.

## M383.3 - Public command deactivation

`python main.py --console` no longer starts an interactive conversation. It
returns a retirement message before configuration, credentials, providers,
residents or lifecycle services are activated.

An explicit embedded call to `main(["--console", ...])` remains temporarily
available as a compatibility seam for historical tests. It is not a supported
user entrypoint and cannot be used by Desktop code.

This separation permits the real console path to retire now while preserving
evidence for shutdown, sanitization and lifecycle behavior until those old tests
are formally archived or replaced.

## M383.4 - Legacy composition isolation

`main.py` no longer contains console runtime construction, resident composition,
owner resolution, Gmail rendering, lifecycle selection or console shutdown.
Those retired responsibilities are isolated in
`app/legacy_console_compatibility.py`.

Three aliases remain injectable in `main.py` solely because certified historical
tests replace them directly: the local conversation builder, console factory and
Gmail announcer. The public command-line guard still prevents real users from
reaching this compatibility module.

`main.py` also retains four inert source strings required by the historical
RP18.8 certification. They are grouped under
`LEGACY_CONSOLE_CERTIFICATION_MARKERS`; they import nothing and cannot construct
or start a runtime.

## M383.5 - Embedded bridge removal

`main.py` now rejects every console request. This includes explicit embedded
calls such as `main(["--console"])`; there is no remaining production bridge to
the historical console library.

The M221 and M228 tests now call the isolated compatibility module directly.
They continue to certify configuration failures, Gmail announcement order,
console construction and clean completion without making those behaviors
reachable from ROBY's entrypoint.

The three injectable aliases previously retained in `main.py` were removed. The
tests now call the isolated compatibility module directly. Only inert RP18.8
source markers remain, and they cannot import or execute any component.

## M383.6 - Parser and marker removal

The production parser no longer defines `--console`. Supplying that option now
fails through the standard unknown-argument behavior before ROBY executes any
application logic.

The RP18.8 test no longer searches `main.py` for obsolete runtime-construction
strings. It verifies instead that official console composition is absent from
the process entrypoint and present only in the isolated historical module.

The four inert certification markers and the dedicated console retirement
message were removed from `main.py`. The entrypoint now contains no console
option, branch, marker, import or call.

## M383.7 - Production configuration decoupling

The production entrypoint no longer accepts `--observe` or `--no-lifecycle`.
Those options configured only the retired console and had no effect on the
Desktop application, maintenance commands or unified cognitive boundary.

`main.py` no longer imports or constructs `DevelopmentConsoleConfig`. The
neutral `--config` path continues to support Desktop startup, `--doctor` and
`--setup` directly.

`DevelopmentConsoleConfig`, `observe_each_turn` and `use_lifecycle` remain only
inside the isolated legacy compatibility module and its historical behavioral
tests. M383.7 does not delete that certified evidence or expose it to production.

## M383.8 - Physical compatibility-bridge removal

`app/legacy_console_compatibility.py`, `DevelopmentConsoleConfig` and the retired
console banner were physically removed. No production code imported them, and
the five tests that exercised only that unreachable composition bridge were
archived.

The doctor, onboarding, setup, configuration and Gmail wiring tests remain on
their canonical components. Runtime lifecycle, shutdown, reserved-input and
observability contracts also remain covered independently.

`LocalConversationConsole` remains temporarily because its module still owns a
local-conversation builder referenced by official composition and because
multiple historical tests certify safety contracts directly on the class. Its
physical deletion requires a separate migration; M383.8 does not broaden the
removal beyond the obsolete compatibility bridge.

## M383.9 - Local-conversation factory separation

`build_local_conversation_from_environment` now lives in
`app/local_conversation_factory.py`. It constructs the local conversation and
its persistence configuration without importing or owning a user interface.

Official runtime composition and the execution-root inventory reference the new
factory path directly. The old console-module path has no compatibility alias,
preventing the retired interface from remaining an architectural dependency.

`LocalConversationConsole` and its independent safety tests remain unchanged.
M383.9 separates construction from presentation but does not yet delete the
historical adapter.

## M383.10 - Remaining console-contract inventory

`LocalConversationConsole` has no production importer. Its remaining references
are limited to six historical suites, classified as follows:

| Contract group | Canonical or independent authority | Remaining evidence |
| --- | --- | --- |
| Input classification | `ConsoleInputParser` | M225.4 parser and reserved-input tests |
| Conversation routing | `OfficialConversationGateway` | RP18.4 route tests |
| Diagnostics | `UnifiedBrainDiagnosticSnapshot` and metadata-only Desktop diagnostics | M182 historical rendering plus M383.2 replacement tests |
| Lifecycle and shutdown | `OfficialROBYRuntime` and Desktop personal runtime | M224.5 historical adapter plus M235 Desktop tests |
| Rendering | Desktop UI and household conversation style | M180/M186 historical adapter assertions |

The six historical suites are now an explicit migration boundary rather than an
accidental production dependency. Physical adapter removal remains deferred
until their console-specific assertions are either archived or re-expressed
against the independent authorities above.

The execution-root key for `main.py` is now `roby_process_entrypoint`; the stale
`development_console` name was removed. This is a naming correction only and
does not alter process startup or runtime behavior.

## M383.11 - Reserved-input boundary migration

`ConsoleInputBoundary` now owns the rule that only input classified as ordinary
conversation may be forwarded to a submission callable. Empty, exit, command
and reserved inputs return without crossing the boundary.

`LocalConversationConsole` delegates classification and forwarding to this
independent component. The M225.4 suite tests reserved-prefix rejection and
normal follow-up directly against the boundary, without importing the historical
adapter.

The allowed historical adapter dependency is therefore reduced from six to
five historical suites. M383.11 changes no Desktop input policy and does not
apply terminal-specific reserved prefixes to ordinary Desktop conversation.

## M383.12 - Single conversation-route migration

RP18.4 now verifies the production `LocalConversationUIAdapter` directly. A
legacy conversation runtime entering that adapter is wrapped by the canonical
`OfficialConversationGateway`, the same boundary used for Desktop text and
voice origins.

The route suite no longer imports or constructs `LocalConversationConsole`.
Console-origin compatibility remains covered by the gateway itself while the
historical adapter exists, but it is no longer required to prove the single
productive conversation route.

The permitted historical adapter dependency is now four historical suites.
No routing, origin accounting or Desktop behavior changes.

## M383.13 - Observability contract migration

M182 no longer imports `LocalConversationConsole`. Its independent observer and
renderer tests remain, including runtime identity, counts, lineage, execution
flags, no extra provider call and content-free rendering.

Seven terminal-command tests for `/status`, `/last`, `/trace`, `/help`, unknown
commands and automatic prompt-reveal output were archived. Those commands are
not a public interface, and prompt-reveal behavior remains retired rather than
being copied into the personal Desktop UI.

Canonical user-facing diagnostics remain the metadata-only
`UnifiedBrainDiagnosticSnapshot` exposed through the Desktop adapter chain.
M383.2 continues to certify that messages, responses and provider prompts are
absent from that view.

The permitted historical adapter dependency is now three historical suites.
No observer gains decision, persistence, retry or execution authority.

## M383.14 - Lifecycle and shutdown contract migration

M224.5 no longer imports `LocalConversationConsole`. Exit commands are tested
directly through `ConsoleInputBoundary`, where they cannot reach conversation
submission.

Lease cleanup is tested on `LongLivedRuntimeLifecycle`: explicit stop reaches
the `STOPPED` state and removes the active lease. Service ordering is tested on
`DesktopPersonalRuntime`, which starts lifecycle, supervisor and residents and
stops them in governed reverse order.

Terminal-reader interruption and retired help-text assertions were archived.
They are not Desktop lifecycle contracts and do not justify preserving the
historical adapter.

The permitted historical adapter dependency is now two historical suites.
Official lifecycle ownership and shutdown behavior remain unchanged.

## M383.15 - Operational input contract migration

M186 no longer imports `LocalConversationConsole`. `/tool` input is classified
as ordinary conversation by `ConsoleInputBoundary` and crosses the boundary
unchanged. Other slash commands remain `COMMAND` input and cannot be submitted
as conversation.

The empty terminal prompt assertion was archived because owner concealment no
longer depends on a removed terminal prompt. Supervisor idempotency, heartbeat
interval, lease recovery, fail-closed behavior and private lease protection
remain tested directly on their independent components.

The permitted adapter dependency is now one historical suite: M180. No runtime,
supervisor, lease or Desktop behavior changes in M383.15.

## M383.16 - Final console-suite migration

M180 no longer imports `LocalConversationConsole`. Completed conversation turns
are submitted and presented through `LocalConversationUIAdapter` with explicit
Desktop origin accounting. Blank input remains non-operational and requests
information without starting the runtime. Failed turns remain explicit as
`[failed]` with failed status.

The EOF test was archived because it described only the removed terminal reader.
The sixteen canonical runtime, persistence, lineage, privacy and mutation tests
remain unchanged; three presentation tests now target the productive Desktop
adapter.

There is now no historical suite importing `LocalConversationConsole`. The
adapter module remains physically present for one final absence audit; physical
adapter deletion is deferred to the next controlled milestone.

## M383.17 - Physical historical-adapter deletion

`app/local_conversation_entrypoint.py` was physically removed after the final
audit confirmed zero production and test importers. No compatibility alias or
replacement console path was added.

The UI-independent conversation factory remains connected to
`OfficialROBYRuntime`. `ConsoleInputBoundary` and the independent trace observer
remain available for the contracts migrated in earlier milestones; neither can
start a terminal interface.

Current RP18.2A and RP18.8 documents now name the factory and official lifecycle
authority directly. Historical manifests and ADRs remain unchanged as records
of prior architecture.

M383 console retirement is complete. ROBY Desktop is the only interactive
interface reachable from the process entrypoint.
