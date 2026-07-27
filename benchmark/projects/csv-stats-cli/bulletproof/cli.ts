import fs from 'node:fs';
import { pathToFileURL } from 'node:url';

export interface ColStat {
  count: number;
  nulls: number;
  mean: number | null;
  min: number | null;
  max: number | null;
  sum: number;
}
export interface Stats {
  rows: number;
  columns: Record<string, ColStat>;
}

/** RFC4180-style parser: handles quoted fields, escaped quotes, and CRLF. */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let field = '';
  let row: string[] = [];
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; } else inQuotes = false;
      } else field += ch;
    } else if (ch === '"') inQuotes = true;
    else if (ch === ',') { row.push(field); field = ''; }
    else if (ch === '\n') { row.push(field); rows.push(row); row = []; field = ''; }
    else if (ch !== '\r') field += ch;
  }
  if (field !== '' || row.length > 0) { row.push(field); rows.push(row); }
  return rows;
}

const round4 = (n: number): number => Math.round((n + Number.EPSILON) * 1e4) / 1e4;

export function computeStats(text: string, only?: string): Stats {
  const table = parseCsv(text);
  if (table.length === 0) return { rows: 0, columns: {} };
  const header = table[0];
  const dataRows = table.slice(1);

  let names = header;
  if (only !== undefined) {
    if (!header.includes(only)) throw new Error(`unknown column: ${only}`);
    names = [only];
  }

  const columns: Record<string, ColStat> = {};
  for (const name of names) {
    const idx = header.indexOf(name);
    const nums: number[] = [];
    let nulls = 0;
    for (const r of dataRows) {
      const cell = (r[idx] ?? '').trim();
      const n = cell === '' ? NaN : Number(cell);
      if (!Number.isFinite(n)) nulls++;
      else nums.push(n);
    }
    const count = nums.length;
    const sum = nums.reduce((a, b) => a + b, 0);
    columns[name] = {
      count,
      nulls,
      mean: count ? round4(sum / count) : null,
      min: count ? Math.min(...nums) : null,
      max: count ? Math.max(...nums) : null,
      sum,
    };
  }
  return { rows: dataRows.length, columns };
}

export function main(argv: string[]): number {
  const args = argv.slice(2);
  let file: string | undefined;
  let only: string | undefined;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--column') only = args[++i];
    else file = args[i];
  }
  if (!file) { console.error('usage: csv-stats <file> [--column NAME]'); return 1; }

  let text: string;
  try {
    text = fs.readFileSync(file, 'utf8');
  } catch {
    console.error(`error: cannot read file: ${file}`);
    return 1;
  }
  try {
    console.log(JSON.stringify(computeStats(text, only)));
    return 0;
  } catch (e) {
    console.error(`error: ${(e as Error).message}`);
    return 1;
  }
}

// Run only when invoked directly (not when imported by unit tests).
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  process.exit(main(process.argv));
}
