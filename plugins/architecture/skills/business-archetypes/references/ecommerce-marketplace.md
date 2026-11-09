# E-commerce and marketplace

**Analogy:** a shopping mall. Many people window-shop (catalog) and a fraction goes in to pay at the till (checkout). The two areas need very different things.

## Dominant forces

- **Massive catalog reads**: search, browsing and product detail dominate the traffic.
- **A correct checkout**: cart, inventory, price, payment and order must be consistent.
- **Campaign peaks** (Black Friday, Hot Sale, paydays).
- In a marketplace, **two sides** (buyers and sellers) with different needs and a fraction of giant sellers.

## Shape of the load (without metrics)

- A very high read-to-write ratio in the catalog; writes concentrated in cart and orders.
- Campaigns with ×5-×20 peaks and discounted products that concentrate the traffic (hot items).
- Scenarios to explore: 10, 1,000 and 100,000 orders per minute at the campaign peak.

## Invariants and consistency

- Do not sell what is not in stock (or, if overselling is accepted, make it an explicit business decision with compensation).
- The price charged is the price shown and confirmed.
- The order, the payment and the inventory reservation are coordinated (saga or orchestration), with compensations.
- Catalog and search: eventual is fine (seconds or minutes of delay).

## Typical subdomains

- **Core**: search and discovery, pricing and promotions, checkout experience; in a marketplace, matching and trust between parties.
- **Supporting**: catalog, inventory, orders, seller management, logistics and shipping.
- **Generic**: payments, notifications, authentication, fraud (often bought).

## Path already walked (check before citing)

- A modular monolith at large scale (Shopify) as an alternative to premature microservices.
- The Dynamo paper (Amazon, 2007) was born from the availability of the shopping cart.
- Search in a dedicated index fed by catalog events.

## Typical failure modes (seed for the red team)

- A campaign hot item: one product's inventory row becomes a bottleneck.
- Search down or slow: the traffic is diverted to the transactional database.
- A half-done saga: payment charged without an order created, or inventory reserved without a payment.
- A stale price cache during a promotion change.
- A giant seller uploading a massive catalog and degrading the others.

## Questions that change the design

- Own inventory, sellers' inventory or both? Is overselling with compensation tolerated?
- How dynamic are prices and promotions?
- What is the campaign calendar and its expected magnitude?
- Are there sellers with disproportionate volumes?

## Hypotheses for a PoC

- Validate the checkout flow end to end with compensations (failures triggered in payment and inventory).
- Validate that catalog and search are decoupled from the transactional database.
- Instrument: conversion per funnel step, search latency, orders in intermediate states, inventory conflicts.
