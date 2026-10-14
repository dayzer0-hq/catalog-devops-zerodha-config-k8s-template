# Zerodha console — separate what changes per environment from the image

`GET /settings` reports every setting the service read, so you can prove a ConfigMap or Secret
actually reached the pod. `GET /healthz` is liveness.

## Every setting it reads, and which are sensitive

| setting | sensitive? | what it does |
|---|---|---|
| `ENVIRONMENT` | no | which environment this is |
| `MARKET_OPEN_IST` | no | when the market opens |
| `MAX_WATCHLIST_SIZE` | no | cap on watchlist entries |
| `FEATURE_BASKET_ORDERS` | no | feature flag |
| `DATABASE_URL` | **yes** | contains the database password |
| `BROKER_API_SECRET` | **yes** | authenticates to the broker API |

The two sensitive ones are reported as `<set>` or `<unset>` and **never echoed**. A debug
endpoint that prints a secret is how a Secret ends up in a log aggregator, so that behaviour is
deliberate and worth keeping when you change this.

## Run it

    ENVIRONMENT=dev BROKER_API_SECRET=anything python3 app/server.py
    curl localhost:8080/settings

## What is deliberately wrong in `k8s/deployment.yaml`

Every value is hardcoded in the manifest, **including both credentials**, which means they are
in git. Three environments means three near-identical copies of this file and a real chance of
deploying staging's database URL to production.

⚠️ One thing to be exact about in your write-up: a Kubernetes Secret is **base64, not
encryption**. `kubectl get secret -o yaml` plus `base64 -d` returns the plaintext to anybody
with read access to the namespace. Moving a credential into a Secret buys you separation from
the image and from the manifest; it does not buy you confidentiality at rest unless the cluster
is configured for it.
