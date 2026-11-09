# Case 06: weak criteria

## Test repo setup

`.scratch/payment-webhook/spec.md`: the service receives webhooks from the payment processor (`payment.captured`, `payment.refunded`), updates the order status and publishes an `order.paid` event that the billing service consumes.

Criteria proposed by the team, in the spec's "Testing decisions" section:

1. "The webhooks endpoint responds 200."
2. "The status is saved in the `orders` table."
3. "The event is published to Kafka."
4. "It works correctly with both event types."

`docs/agents/qa.md`: solo mode.

## Instruction to the agent

"Clean up the acceptance criteria of this spec."
