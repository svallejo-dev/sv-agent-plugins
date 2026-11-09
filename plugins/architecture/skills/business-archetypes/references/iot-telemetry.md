# IoT and telemetry

**Analogy:** a network of rain gauges. Thousands of devices send a small measurement every few seconds, without stopping; almost nobody looks at each data point, but everyone wants the trends and the alarms.

## Dominant forces

- **Continuous ingestion of small writes**: write volume dominates over reads.
- **Time series**: data is queried by time range and aggregated; recent data is worth more than old data.
- **Unreliable devices**: intermittent connectivity, skewed clocks, old firmware.
- **Commands to the devices** (configuration, updates) with guaranteed delivery.

## Shape of the load (without metrics)

- Key formula: **writes/s ≈ devices × send frequency**; bytes ≈ that × message size.
- Reconnection peaks: after an outage, every device sends its backlog at once.
- Scenarios to explore: 1k, 100k and 10M devices, sending every 1, 10 and 60 seconds.

## Invariants and consistency

- Measurements can arrive late, duplicated and out of order: the system must order by the event timestamp (careful with skewed clocks) and deduplicate.
- Critical alarms with bounded latency.
- Tiered retention: raw data for a short time, aggregates for a long time (downsampling).

## Typical subdomains

- **Core**: the analysis and alarms that bring value (predictive maintenance, monitoring).
- **Supporting**: device registration and provisioning, firmware management, dashboards.
- **Generic**: messaging broker (MQTT), time-series storage, device identity.

## Path already walked (check before citing)

- MQTT as a lightweight publish/subscribe protocol for devices.
- Time-series databases with downsampling and tiered retention.
- Edge processing to filter and aggregate before sending.

## Typical failure modes (seed for the red team)

- Mass reconnection after an outage: every device's backlog at once.
- A faulty device sending at 100× its frequency.
- Skewed clocks that pollute the series and trigger false alarms.
- Storage that grows without downsampling or retention.
- A firmware update that bricks a fleet.

## Questions that change the design

- How many devices and at what frequency? How long can they be disconnected?
- Which decisions must be made in real time and which on aggregates?
- How long is raw data kept?
- Can the devices receive commands? With what guarantee?

## Hypotheses for a PoC

- Validate ingestion with a device simulator that includes disconnections, duplicates and out-of-order data.
- Validate the storage cost per device per month with the proposed retention.
- Instrument: messages per second per device, ingestion lag, out-of-order events, silent devices.
