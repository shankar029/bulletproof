/**
 * Search Guard — rule definitions.
 *
 * Dependency-free on purpose: no pi imports, so the rules can be unit-tested directly.
 * The pi binding lives in index.ts.
 */

export const ESCAPE_HATCH = "#allow-slow-search";

/** Command boundary: start of string, or after a shell separator. */
const B = String.raw`(?:^|[\s;&|(\`])`;

export interface Rule {
	id: string;
	test: RegExp;
	/** Returns true to waive the rule for this specific command. */
	waive?: (command: string) => boolean;
	message: string;
}

export const RULES: Rule[] = [
	{
		id: "recursive-grep",
		// grep with -r / -R anywhere in a short-flag cluster (-r, -rn, -rl, -nr), or --recursive.
		// The trailing [A-Za-z]* matters: without it, `-rn` cannot match, because [A-Za-z]*
		// consumes "rn" and the following \b then fails mid-cluster.
		test: new RegExp(
			`${B}grep\\b[^|;&]*?(?:\\s-[A-Za-z]*[rR][A-Za-z]*\\b|\\s--recursive\\b)`,
		),
		message:
			"`grep -r` walks the entire tree and does not return on this repo.\n" +
			"Use the `grep` tool (fast, git-aware, frecency-ranked), or if you must shell out:\n" +
			'  rg -t cs -t ts "<pattern>"            # restrict by file type\n' +
			'  rg "<pattern>" <subtree>              # restrict by subtree\n' +
			"`rg` is already on PATH and honours the repo's .ignore file.",
	},
	{
		id: "include-glob-all",
		test: /--include=(\*|"\*"|'\*')(\s|$)/,
		message:
			"`--include=*` matches every file, including committed binaries.\n" +
			"Use `rg -t <type>` or pass an explicit glob such as `rg -g '*.cs' \"<pattern>\"`.",
	},
	{
		id: "recursive-find",
		// find rooted at ., /, ~ or a drive letter — unbounded unless depth-limited.
		test: new RegExp(`${B}find\\s+(?:\\.|/|~|[A-Za-z]:)`),
		// A shallow -maxdepth is bounded, so allow it.
		waive: (command) => {
			const m = command.match(/-maxdepth\s+(\d+)/);
			return m !== null && Number(m[1]) <= 3;
		},
		message:
			"`find .` walks every directory in the repo.\n" +
			"Use the `find` tool, or if you must shell out:\n" +
			"  fd -g '<glob>'                        # already on PATH, honours .ignore\n" +
			"  find . -maxdepth 3 ...                # a shallow scan is allowed",
	},
	{
		id: "recursive-ls",
		test: new RegExp(`${B}ls\\s+-[A-Za-z]*R\\b`),
		message:
			"`ls -R` walks the whole tree. Use `fd -g '<glob>'` or the `find` tool instead.",
	},
	{
		id: "windows-recursive-dir",
		test: new RegExp(`${B}dir\\b[^|;&]*\\s/s\\b`, "i"),
		message: "`dir /s` walks the whole tree. Use `fd -g '<glob>'` instead.",
	},
];

/** `git grep` is index-backed and fast — never block it. */
const GIT_GREP = new RegExp(`${B}git\\s+grep\\b`);

/** Returns the violated rule, or undefined when the command is acceptable. */
export function evaluate(command: string): Rule | undefined {
	if (command.includes(ESCAPE_HATCH)) return undefined;
	if (GIT_GREP.test(command)) return undefined;
	return RULES.find(
		(rule) => rule.test.test(command) && rule.waive?.(command) !== true,
	);
}

/** The message shown to the model when a command is blocked. */
export function blockReason(rule: Rule): string {
	return (
		`Blocked by search-guard (${rule.id}).\n\n${rule.message}\n\n` +
		`If a full scan is genuinely required, re-run with ${ESCAPE_HATCH} appended to the command.`
	);
}

// ---------------------------------------------------------------------------
// Default bash timeouts
// ---------------------------------------------------------------------------
//
// pi's bash tool declares `timeout` as optional with **no default**, so a command that never
// returns hangs its agent forever: the tool never settles, `tool_execution_end` is never
// emitted, the child never reaches `agent_end`, and the parent waits indefinitely with no
// signal. Blocking known-slow search patterns only covers the cases we can name; a locked
// NuGet cache, a proxied `npm ci`, or a git operation waiting on credentials wedges just as
// hard and is not pattern-matchable.
//
// So every bash call gets a wall-clock bound. A model-supplied `timeout` always wins - this
// only fills in the blank.

/** Ordinary commands: seconds. */
export const DEFAULT_TIMEOUT_S = 300;

/** Builds, installs and test suites legitimately run long: seconds. */
export const LONG_TIMEOUT_S = 1800;

/**
 * Commands that routinely exceed the ordinary bound. Matching one raises the ceiling rather
 * than removing it - an 1800s failure is still recoverable, an unbounded hang is not.
 */
const LONG_RUNNING = new RegExp(
	[
		// package managers
		`${B}(?:npm|pnpm|yarn|bun)\\s+(?:ci|install|i|add|update|run\\s+\\S+)\\b`,
		`${B}(?:pip|pip3|poetry|uv)\\s+(?:install|sync|add)\\b`,
		`${B}(?:nuget|dotnet)\\s+restore\\b`,
		// builds
		`${B}dotnet\\s+(?:build|publish|test|pack)\\b`,
		`${B}(?:msbuild|cargo|gradle|gradlew|mvn|make|cmake|ninja|bazel|tsc|webpack|vite)\\b`,
		// test runners
		`${B}(?:pytest|vitest|jest|mocha|playwright|cypress|ctest|go\\s+test)\\b`,
		// containers / browsers
		`${B}docker\\s+(?:build|compose)\\b`,
		`${B}npx\\s+playwright\\s+install\\b`,
		// agent-browser downloads Chrome for Testing on first run; everything else it does
		// (navigate, snapshot, click) is sub-second and keeps the ordinary bound, which is what
		// stops a wedged browser daemon from hanging a verification run.
		`${B}agent-browser\\s+install\\b`,
		// the project's own idle-timeout runner already bounds itself
		`${B}python\\s+\\S*run\\.py\\b`,
	].join("|"),
	"i",
);

/** Wall-clock bound in seconds for a bash command that did not specify one. */
export function defaultTimeoutSeconds(command: string): number {
	return LONG_RUNNING.test(command) ? LONG_TIMEOUT_S : DEFAULT_TIMEOUT_S;
}
