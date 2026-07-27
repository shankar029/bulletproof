export interface Order { status: string; }

export function createOrder(): Order {
  return { status: 'cart' };
}

// Switch-style transitions with logic duplicated between `transition` and `can`. The `cancel`
// branch fires from ANY state — a real bug — and there is no way to add a transition without
// editing this function.
export function transition(order: Order, event: string): Order {
  const s = order.status;
  if (event === 'place' && s === 'cart') order.status = 'placed';
  else if (event === 'pay' && s === 'placed') order.status = 'paid';
  else if (event === 'ship' && s === 'paid') order.status = 'shipped';
  else if (event === 'deliver' && s === 'shipped') order.status = 'delivered';
  else if (event === 'cancel') order.status = 'cancelled'; // BUG: allowed from any state
  else throw new Error(`invalid transition: ${event} from ${s}`);
  return order;
}

export function can(order: Order, event: string): boolean {
  const s = order.status;
  if (event === 'place') return s === 'cart';
  if (event === 'pay') return s === 'placed';
  if (event === 'ship') return s === 'paid';
  if (event === 'deliver') return s === 'shipped';
  if (event === 'cancel') return true; // BUG: same over-permissive cancel
  return false;
}
