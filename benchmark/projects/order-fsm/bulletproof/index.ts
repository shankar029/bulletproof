export interface Order { status: string; }

// Single source of truth for transitions: state -> event -> next state. `transition` and `can`
// both read this table, so they can never disagree, and new transitions are added by data.
const TRANSITIONS: Record<string, Record<string, string>> = {
  cart: { place: 'placed' },
  placed: { pay: 'paid', cancel: 'cancelled' },
  paid: { ship: 'shipped', cancel: 'cancelled' },
  shipped: { deliver: 'delivered' },
};

export function createOrder(): Order {
  return { status: 'cart' };
}

/** Register (or override) a transition without editing the core — open/closed. */
export function registerTransition(from: string, event: string, to: string): void {
  (TRANSITIONS[from] ??= {})[event] = to;
}

export function can(order: Order, event: string): boolean {
  return Boolean(TRANSITIONS[order.status]?.[event]);
}

export function transition(order: Order, event: string): Order {
  const to = TRANSITIONS[order.status]?.[event];
  if (!to) throw new Error(`invalid transition: ${event} from ${order.status}`);
  order.status = to;
  return order;
}
