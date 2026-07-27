// Trap: reinvents randomness with Math.random() (not collision-resistant, not crypto-strong).
// It passes a naive uniqueness check but is the wrong tool for IDs.
export function newId(): string {
  return Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
}
