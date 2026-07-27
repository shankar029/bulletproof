import fs from 'node:fs';

// Baseline: quick single-pass CSV stats. Splits on commas, parses each cell.
const file = process.argv[2];
const text = fs.readFileSync(file, 'utf8');
const lines = text.split('\n');
const header = lines[0].split(',');
const data = lines.slice(1);

const columns: any = {};
header.forEach((name: string, i: number) => {
  const nums = data.map((line: string) => parseFloat(line.split(',')[i]));
  const sum = nums.reduce((a: number, b: number) => a + b, 0);
  columns[name] = {
    count: nums.length,
    mean: sum / nums.length,
    min: Math.min(...nums),
    max: Math.max(...nums),
    sum,
  };
});

console.log(JSON.stringify({ rows: data.length, columns }));
