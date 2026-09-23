/**
 * Search Guard
 *
 * Blocks pathological repo-wide shell searches before they run and tells the model
 * what to use instead.
 *
 * Why this exists: a subagent researching this repo issued
 *
 *     grep -rn "he-vs-assign-panel" --include=* -l . | grep -v node_modules
 *
 * which scans every file in the tree (the `grep -v` filter runs far too late) including a
 * committed 29MB installer. It never returned. The per-tool deadline fired at 300s and the
 * whole research run was lost. Measured alternatives on the same query:
 *
 *     grep -r ...            > 300s (killed)
 *     rg (default)             32.2s
 *     rg -t cs -t ts -t js      1.0s
 *     rg <subtree>              0.3s
 *     grep tool (fff)         instant
 *
 * Prompt rules did not prevent this: that agent had a working `grep` tool, used it
 * successfully, and then shelled out to `grep -r` anyway. So this is a hard block, not advice.
 *
 * Escape hatch: append `#allow-slow-search` to the command when a full scan is genuinely
 * intended (e.g. searching ignored or binary files).
 *
 * It also fills in a default wall-clock `timeout` on every bash call. pi's bash tool has no
 * default, so any command that never returns wedges its agent permanently — blocking the four
 * search patterns we can name does nothing for a locked package cache or a git operation
 * waiting on credentials. A model-supplied timeout always wins.
 */

import {
 isToolCallEventType,
 type ExtensionAPI,
} from "@earendil-works/pi-coding-agent";
import { blockReason, defaultTimeoutSeconds, evaluate } from "./rules.ts";

export default function (pi: ExtensionAPI) {
 pi.on("tool_call", (event) => {
  if (!isToolCallEventType("bash", event)) return;

  const command = event.input?.command;
  if (typeof command !== "string" || command.length === 0) return;

  const violated = evaluate(command);
  if (violated) return { block: true, reason: blockReason(violated) };

  // Bound anything the model left unbounded. Never shorten an explicit value.
  if (
   typeof event.input.timeout !== "number" ||
   !Number.isFinite(event.input.timeout)
  ) {
   event.input.timeout = defaultTimeoutSeconds(command);
  }
 });
}
