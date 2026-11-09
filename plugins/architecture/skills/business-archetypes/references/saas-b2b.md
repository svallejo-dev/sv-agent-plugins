# Multi-tenant B2B SaaS

**Analogy:** a shared office building. Each company has its own space, but they share elevators, electricity and the front desk; a company that grows a lot cannot leave the others without an elevator.

## Dominant forces

- **Isolation between tenants**: of data (security), of performance (noisy neighbor) and of failures (blast radius).
- **A very skewed size distribution**: many small customers and a few huge ones that generate most of the revenue and the load.
- **Per-tenant customization and configuration** without forking the code.
- **Enterprise requirements**: SSO, auditing, data residency, contractual SLAs.

## Shape of the load (without metrics)

- The customers' business hours (peaks per time zone) and batch processes (imports, reports, integrations).
- One large tenant can generate more load than thousands of small ones together.
- Scenarios to explore: 100, 10,000 and 1M tenants, with one tenant that is 1,000 times the average.

## Invariants and consistency

- **No tenant sees another's data**: it is the most important invariant; the tenant_id in every query, with defense in depth (row-level security, mandatory scoping in the data layer).
- Per-tenant limits and quotas applied consistently.
- Auditing of actions per user and tenant.

## Typical subdomains

- **Core**: the product's functionality (what the customer buys).
- **Supporting**: tenant management and configuration, usage-based billing, integrations, reports.
- **Generic**: identity and SSO, notifications, payments.

## Path already walked (check before citing)

- Silo (dedicated resources per tenant), pool (everything shared) and bridge (mixed) isolation models, according to AWS's SaaS guidance.
- Metadata-driven multi-tenant architecture (Salesforce).
- Sharding by tenant and the migration to Vitess at large scale (Slack).
- Cells to limit the blast radius of a tenant or a deploy.

## Typical failure modes (seed for the red team)

- A data leak between tenants through a query without a tenant filter.
- Noisy neighbor: a tenant with a massive import degrades everyone.
- A schema migration that takes hours on the largest tenant's database.
- A huge tenant that no longer fits in the shared shard.
- A bad deploy that affects every customer at once.

## Questions that change the design

- What isolation do the large customers demand (dedicated database, dedicated region, encryption with their own key)?
- How is it billed: per seat, per usage, per plan?
- How different is the configuration between tenants?
- Are there data residency requirements per country?

## Hypotheses for a PoC

- Validate data isolation with tests that try to access another tenant.
- Validate per-tenant quotas and rate limits with a huge synthetic tenant.
- Instrument everything per tenant from day one (latency, errors, consumption): without that you cannot detect the noisy neighbor or bill by usage.
