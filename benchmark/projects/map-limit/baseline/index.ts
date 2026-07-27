// Naive: ignores `limit` entirely and runs every worker at once. Passes the order and rejection
// cases but blows the concurrency bound — the one thing this function exists to enforce.
export function mapLimit<T, R>(
  items: T[],
  limit: number,
  worker: (item: T, index: number) => Promise<R>,
): Promise<R[]> {
  return Promise.all(items.map((item, i) => worker(item, i)));
}
