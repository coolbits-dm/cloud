# _SANDBOX Overview

## Stripe Integration (Sandbox)
Stripe CLI configured on COOL BITS SRL (Test mode)
Webhook endpoint: https://stripe.coolbits.ai/webhook
To trigger test events:
  stripe trigger payment_intent.succeeded

Env variables are declared in `.env` (mirrors `.env.example` in the repo root); keep the values in sync so the webhook authentication stays stable.
The webhook endpoint is globally active for the sandbox account, and every test event is immediately routed to the Cool Bits relay.
