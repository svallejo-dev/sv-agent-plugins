# Mobility, logistics and geolocation

**Analogy:** a taxi dispatch center with a live map. The pieces (drivers, parcels) move all the time and the center must pair each request with the right piece in seconds.

## Dominant forces

- **Real-time geospatial state**: locations that change every few seconds.
- **Matching** between supply and demand (driver-rider, courier-order) with distance and time constraints.
- **A contested scarce resource**: two requests cannot be assigned to the same driver at once.
- Highly variable demand by zone and hour (rain, events, rush hours).

## Shape of the load (without metrics)

- Key formula: **location updates/s ≈ active agents ÷ send interval**.
- Geographic concentration: the city's hot spots concentrate the load.
- Scenarios to explore: 1k, 100k and 1M active agents sending their location every 4-5 seconds.

## Invariants and consistency

- An agent is assigned to only one request at a time (consistency in the assignment).
- Locations can be eventual and approximate; the last known position is worth more than the history.
- Dynamic prices stay coherent during the quote and the trip.

## Typical subdomains

- **Core**: matching and dispatch, dynamic pricing, arrival time estimation.
- **Supporting**: trip or shipment management, agent profiles, support.
- **Generic**: maps and routing (often bought), payments, notifications.

## Path already walked (check before citing)

- Hierarchical geospatial indexes: geohash, S2 (Google) and H3 (Uber's hexagonal index).
- In-memory location state partitioned by geographic cell.
- Dynamic pricing per zone according to the supply/demand ratio.

## Typical failure modes (seed for the red team)

- A hot cell (a stadium when an event ends) that concentrates the load in one partition.
- Double assignment of an agent because of a race in the matching.
- A maps or routing provider that is slow or has its quota exhausted.
- Mobile clients with a bad signal retrying in bursts.
- Loss of a geographic partition's in-memory state.

## Questions that change the design

- How many active agents at rush hour and how often do they send their location?
- How fast must a matching be resolved?
- Own maps and routing or a provider's? With which quotas?
- Is the business per city (partitionable) or does it need a global view?

## Hypotheses for a PoC

- Validate the matching with a simulation of agents and requests in one city, with hot zones.
- Validate the maps provider's cost and quotas at the expected volume.
- Instrument: matching time, conflicting assignments, location freshness, load per cell.
