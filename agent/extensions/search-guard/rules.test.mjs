import {
  DEFAULT_TIMEOUT_S,
  LONG_TIMEOUT_S,
  defaultTimeoutSeconds,
  evaluate,
} from "./rules.ts";

const cases = [
  // [command, shouldBlock, note]
  [
    'grep -rn "he-vs-assign-panel" --include=* -l . | grep -v node_modules',
    true,
    "the real wedge",
  ],
  ['cd /c/x; grep -rn "ActionId" src/', true, "after separator"],
  ["grep -R foo .", true, "-R"],
  ["grep --recursive foo .", true, "--recursive"],
  ["grep -rl foo .", true, "-rl cluster"],
  ['find . -name "*AssignVsLicense*"', true, "find ."],
  ["find / -name x", true, "find /"],
  ["ls -R", true, "ls -R"],
  ["dir /s *.cs", true, "windows dir /s"],
  ['rg -t cs "ActionId"', false, "rg typed"],
  ['fd -g "*.cs"', false, "fd"],
  ['git grep -n "ActionId"', false, "git grep is fast"],
  ['grep -n "ActionId" file.cs', false, "non-recursive grep"],
  ["rg -l foo | grep -v node_modules", false, "grep as a pipe filter"],
  ["cat findings.txt", false, "word 'find' inside a filename"],
  // Accepted over-block: we do not shell-parse quotes. Blocking an echo is harmless and
  // the escape hatch covers it; under-blocking a real `find .` is not harmless.
  ['echo "please find . something"', true, "quoted find: accepted over-block"],
  ['find . -maxdepth 2 -name "*.json"', false, "shallow find allowed"],
  ["find . -maxdepth 9 -name x", true, "deep maxdepth still blocked"],
  ["grep -rn foo . #allow-slow-search", false, "escape hatch"],
  ["git log --oneline -1", false, "git log"],
  ["dotnet test", false, "unrelated"],
  ["npm run build", false, "unrelated"],
];

let pass = 0,
  fail = 0;
for (const [cmd, expect, note] of cases) {
  const r = evaluate(cmd);
  const blocked = r !== undefined;
  const ok = blocked === expect;
  if (ok) {
    pass++;
  } else {
    fail++;
  }
  console.log(
    `${ok ? "PASS" : "FAIL"}  blocked=${String(blocked).padEnd(5)} want=${String(expect).padEnd(5)} ${(r?.id ?? "-").padEnd(22)} ${note}`,
  );
}
// --- default bash timeouts -------------------------------------------------
const timeoutCases = [
  // [command, expected seconds, note]
  ['rg -t cs "ActionId"', DEFAULT_TIMEOUT_S, "ordinary command"],
  ["git log --oneline -1", DEFAULT_TIMEOUT_S, "git log"],
  ["cat foo.txt", DEFAULT_TIMEOUT_S, "cat"],
  ["npm ci", LONG_TIMEOUT_S, "npm ci"],
  ["npm run build", LONG_TIMEOUT_S, "npm run build"],
  ["dotnet build", LONG_TIMEOUT_S, "dotnet build"],
  ["dotnet test --no-build", LONG_TIMEOUT_S, "dotnet test"],
  ["cd src && dotnet restore", LONG_TIMEOUT_S, "after separator"],
  ["npx playwright install chromium", LONG_TIMEOUT_S, "playwright install"],
  ["pytest -q", LONG_TIMEOUT_S, "pytest"],
  [
    "python scripts/run.py --idle 60 -- npm test",
    LONG_TIMEOUT_S,
    "idle runner",
  ],
  ["docker build .", LONG_TIMEOUT_S, "docker build"],
  ["composer install", LONG_TIMEOUT_S, "php composer"],
  ["bundle install", LONG_TIMEOUT_S, "ruby bundler"],
  ["go mod download", LONG_TIMEOUT_S, "go modules"],
  ["go build ./...", LONG_TIMEOUT_S, "go build"],
  ["mix deps.get", LONG_TIMEOUT_S, "elixir mix"],
  ["./gradlew test", LONG_TIMEOUT_S, "gradle wrapper"],
  ["rspec", LONG_TIMEOUT_S, "ruby rspec"],
  ["sbt compile", LONG_TIMEOUT_S, "scala sbt"],
  ["swift test", LONG_TIMEOUT_S, "swift test"],
  ["rake", LONG_TIMEOUT_S, "rake task runner"],
  [
    "agent-browser install",
    LONG_TIMEOUT_S,
    "agent-browser install (downloads Chrome)",
  ],
  [
    "agent-browser install --with-deps",
    LONG_TIMEOUT_S,
    "agent-browser install --with-deps",
  ],
  [
    "agent-browser navigate http://localhost:5173",
    DEFAULT_TIMEOUT_S,
    "agent-browser drive stays bounded",
  ],
  [
    "agent-browser snapshot",
    DEFAULT_TIMEOUT_S,
    "agent-browser snapshot stays bounded",
  ],
  // Not an over-match: the quote before `npm` is not a command boundary, so this correctly
  // gets the ordinary bound. (Contrast the block rules, where `find` after a space inside a
  // quoted string does match and is accepted as an over-block.)
  [
    'echo "npm ci is what I would run"',
    DEFAULT_TIMEOUT_S,
    "quoted: correctly not treated as a build",
  ],
];
for (const [cmd, want, note] of timeoutCases) {
  const got = defaultTimeoutSeconds(cmd);
  const ok = got === want;
  if (ok) {
    pass++;
  } else {
    fail++;
  }
  console.log(
    `${ok ? "PASS" : "FAIL"}  timeout=${String(got).padEnd(6)} want=${String(want).padEnd(6)} ${"".padEnd(17)} ${note}`,
  );
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
