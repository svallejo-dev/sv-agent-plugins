# Ticketing, bookings and flash sales

**Analogy:** the doors opening at a concert. For months nobody arrives; in one minute everyone arrives at once and there is room for only a fraction.

## Dominant forces

- **Demand far above supply** in short windows: the problem is not the average, it is the opening minute.
- **Contention over scarce inventory**: many users compete for the same rows (seats, slots, rooms).
- **Perceived fairness and bots**: who gets in first and who is left out is a business and reputation problem.
- Most of the time the system is almost idle.

## Shape of the load (without metrics)

- An extreme and predictable peak (the opening time is known), with peaks of ×100 or more over a normal day.
- Massive availability reads and writes concentrated on a few hot rows.
- Scenarios to explore: 1k, 100k and 1M users trying to buy in the same minute, against an inventory of thousands.

## Invariants and consistency

- **No overselling**: the inventory sold never exceeds what is available. Strong consistency in the allocation.
- **Temporary holds** with expiration: the seat is locked while the user pays and released if they do not.
- Payment and ticket issuance tied together: no ticket without a confirmed payment and no payment without a ticket.

## Typical subdomains

- **Core**: inventory allocation and holds, purchase queue management, bot prevention.
- **Supporting**: catalog of events and venues, seat maps, ticket issuance and validation.
- **Generic**: payments, notifications, authentication.

## Path already walked (check before citing)

- Virtual waiting rooms that admit users to the store at a rate the backend can sustain.
- Holds with a TTL and automatic release.
- Public failures of big presales (for example, Ticketmaster's 2022 presale) as a case study of demand and bots.

## Typical failure modes (seed for the red team)

- All the opening traffic hits the inventory database directly.
- Hot rows: thousands of transactions locking the same rows.
- Holds that do not expire (cleanup process down): phantom inventory sold out.
- Bots hoarding the inventory or saturating the queue.
- The payment gateway becomes the bottleneck at the peak.

## Questions that change the design

- Numbered seats or general admission? (it changes the granularity of the contention)
- How long does a hold last and what happens if the payment arrives late?
- Is an explicit waiting queue acceptable for the user?
- Which anti-bot and per-user limit policy does the business require?

## Hypotheses for a PoC

- Validate the no-overselling invariant under real concurrency (a load test aimed at the same rows) before anything else.
- Validate that the waiting room protects the backend: controlled, measurable admission.
- Instrument: users in queue, admission rate, active and expired holds, allocation conflicts, hold-to-payment conversion.
