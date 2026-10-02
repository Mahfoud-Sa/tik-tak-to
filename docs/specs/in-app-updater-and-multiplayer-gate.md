## Problem Statement

Players running older versions of XO Game have no seamless way to update their game binaries directly from within the application. Currently, clicking "Download Update" simply launches an external web browser, forcing players to manually locate downloaded zip files, extract them, and manually replace the running executable. Furthermore, when critical multiplayer protocol changes or mandatory bug fixes are published, older clients can either encounter silent network incompatibilities or bypass mandatory updates by closing the update dialog, resulting in broken multiplayer sessions. Conversely, aggressively blocking the entire application for mandatory updates frustrates players who simply wish to play offline pass-and-play games on their local machine. Additionally, running update checks on every window focus event causes unnecessary background requests and resource churn.

## Solution

A robust, integrated In-App Patcher and feature-gated update lifecycle:
1. When updates are published, the game checks for updates 2 seconds after startup or upon explicit manual request via the Help menu, eliminating noisy window-focus polling.
2. If an optional update is available, the player can choose to install it immediately or dismiss it for later without repeated prompts.
3. If a mandatory update is pending, the player is informed that online multiplayer requires updating, but offline local pass-and-play remains accessible. Attempting to start a multiplayer session triggers a clear upgrade modal.
4. Clicking to update initiates an in-app download with visual progress reporting and cryptographic SHA-256 verification.
5. In production, an external updater script safely stages the new executable, waits for the running game to terminate, swaps the binary, and relaunches the game seamlessly. In development mode, the game safely delegates to the browser fallback without altering the Python environment.

## User Stories

1. As a desktop player, I want the game to automatically check for updates shortly after launch, so that I am promptly aware when a new version is available without having to remember to check manually.
2. As a desktop player, I want to manually check for updates via the Help menu at any time, so that I can immediately verify whether my installation is on the latest release.
3. As a desktop player, I want manual update checks to give clear feedback when my game is already up to date, so that I know my version is current.
4. As a desktop player, I want manual update checks to display a friendly warning if the update servers cannot be reached, so that I understand there was a network failure without technical confusion.
5. As a desktop player, I want silent startup update checks to fail silently without modal alerts if there is no internet connection, so that my offline gaming experience is completely uninterrupted.
6. As a desktop player, I want update checks not to trigger every time I alt-tab or focus the window, so that my system is not bombarded with redundant network requests.
7. As a desktop player, I want to view clear release highlights in the update notification dialog, so that I understand what new features or bug fixes are included in the new release.
8. As a desktop player, I want to dismiss optional updates by clicking "Later", so that the game does not bother me again on subsequent launches for that specific version.
9. As a desktop player, I want mandatory updates to prevent me from entering online multiplayer games, so that I do not encounter network desyncs or protocol crashes against updated servers.
10. As a desktop player, I want mandatory updates to allow local two-player offline play, so that I can still enjoy the game with a friend on the same machine even if I cannot update immediately.
11. As a desktop player, I want to see an explanatory upgrade prompt if I attempt to click the Multiplayer button while a mandatory update is pending, so that I know why it is restricted and have a one-click button to update.
12. As a desktop player, I want the update dialog to download the new version directly inside the application, so that I do not have to leave the game or manually browse external websites.
13. As a desktop player, I want to see a live progress bar indicating downloaded bytes, total file size, and percentage during an update download, so that I know the download is actively proceeding.
14. As a desktop player, I want the option to cancel an ongoing update download, so that I can regain bandwidth or postpone the update if needed.
15. As a desktop player, I want the application to verify the SHA-256 checksum of the downloaded update before applying it, so that corrupted or truncated files are never executed on my machine.
16. As a desktop player, I want the application to automatically terminate, apply the replacement executable, and relaunch the updated game, so that the upgrade process is completely automated.
17. As a desktop player, I want a graceful fallback to a manual browser download if in-app extraction or file replacement encounters unexpected OS permission errors, so that I am never left without a way to get the latest version.
18. As a developer running from source, I want the in-app patcher to detect that the game is running in a development Python environment and open the browser download instead of attempting to overwrite my Python interpreter, so that my development environment remains intact.
19. As a player on the stable channel, I want the game to ignore prerelease and beta versions by default, so that I only receive thoroughly tested releases.

## Implementation Decisions

- **Update Polling Lifecycle**: Update checks are initiated strictly at startup (2-second delayed asynchronous check) and on-demand through the Help menu. The window focus event listener is removed entirely to prevent unintended network polling.
- **Mandatory Update Feature Gate**: A mandatory update state flag is maintained in the application state. When this flag is active, local two-player game initiation is allowed, but multiplayer entry points intercept the action and present an upgrade modal with actions to "Update Now" or "Cancel".
- **In-App Download Engine**: The update service is extended with an asynchronous, chunk-based download method that emits byte progress events to a UI listener and supports user cancellation via an abort flag.
- **Cryptographic Integrity Verification**: Upon download completion, the updater computes the SHA-256 digest of the temporary archive and compares it with the digest specified in the update manifest. If a mismatch occurs, the temporary archive is purged, and the user is alerted with an option to download manually via browser.
- **Environment Detection Guardrail**: The update engine checks if the runtime is running as a frozen executable (packaged application). If running unfrozen from source code, in-app file replacement is bypassed, and the browser fallback is invoked to preserve the host Python environment.
- **External Batch Runner for Windows Executable Replacement**: Because running Windows executables are locked by the operating system, the application writes a self-contained batch script in the system temporary directory. When the user confirms installation, the application launches the batch runner detached and terminates itself. The batch script polls until the main game process exits, extracts the executable from the validated zip, moves it over the target executable path, relaunches the updated game, and deletes the temporary script.
- **Progressive UI Transformation**: The update notification dialog transforms its action button region to show a progress bar, downloaded size metrics, and a Cancel button once download begins.
- **Channel Policy**: The desktop client defaults to and strictly enforces the stable release channel.

## Testing Decisions

- **What makes a good test**: Tests must verify externally observable behavior and state transitions through clear interface seams, rather than asserting on private internal loop variables or Tkinter visual layout geometry.
- **Modules to be tested**:
  - The update evaluation engine: verifying correct classification of mandatory versus optional updates, SemVer precedence, dismissal persistence, and channel filtering.
  - The download and verification pipeline: verifying chunked downloading, cancel signaling, SHA-256 checksum matching and mismatch handling, using mock HTTP servers or local file URLs.
  - The updater launcher script generation: verifying that the generated Windows batch script contains correct path escaping, process waiting logic, and relaunch commands.
  - The multiplayer gating coordinator: verifying that flagging a mandatory update permits local game startup while intercepting multiplayer initialization with the expected lockout response.
- **Prior Art**: Existing unit tests in the project test suite verify SemVer comparison, manifest deserialization, and dismissal persistence. New tests will follow this exact pattern using the standard test runner.

## Out of Scope

- Differential / delta binary patching (e.g., Courgette or bsdiff); releases are distributed as full standalone executable archives.
- Automated code signing certificates or SmartScreen reputation registration.
- In-game UI for switching between release channels (e.g., Beta opt-in); client remains strictly stable.
- Linux and macOS binary packaging or in-app self-updating; Windows x64 desktop is the sole target desktop platform.

## Further Notes

- Architectural context and rationale are recorded in ADR 0001 (In-App Patcher and Multiplayer Lockout).
- Domain terms (Update Manifest, Mandatory Update, In-App Patcher, Dismissed Version) are documented in the root domain glossary.
