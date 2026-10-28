# Primeagent on Grafana + Loki

Reference stack that ingests Primeagent's structured JSON logs into [Loki](https://grafana.com/oss/loki/) and visualizes them with a pre-provisioned Grafana dashboard.

Use this as a starting point. The compose file, Alloy config, dashboard JSON, and legacy Promtail configuration are independent of the rest of `deploy/` and can be lifted into any environment.

[Grafana Alloy](https://grafana.com/oss/alloy/) replaced [Promtail](https://grafana.com/docs/alloy/latest/set-up/migrate/from-promtail/), which reached end of life on March 2, 2026.

## What you get

- **Loki 3.2** on `:3100`
- **Alloy 1.18** scraping a directory of Primeagent log files
- **Grafana 11.3** on `:3000` with the Loki datasource and the `Primeagent Logs` dashboard already provisioned

## Prerequisites on the Primeagent side

The dashboard expects Primeagent to be running in JSON mode with service metadata set. At minimum:

```bash
PRIMEAGENT_LOG_ENV=container
PRIMEAGENT_LOG_FILE=/absolute/path/to/primeagent/logs/primeagent.log
PRIMEAGENT_SERVICE_NAME=primeagent
PRIMEAGENT_VERSION=1.10.0
PRIMEAGENT_ENVIRONMENT=production
```

Alloy scrapes a directory of `*.log` files, so `PRIMEAGENT_LOG_FILE` must point at a file inside the directory you expose to Alloy as `PRIMEAGENT_LOG_DIR` (see [Run](#run)). Set both to the same directory, otherwise Alloy watches an empty folder and the dashboard stays blank. Use an absolute path: `PRIMEAGENT_LOG_FILE` is resolved against Primeagent's working directory, not this one.

In JSON mode the file is a single JSON stream: application logs and third-party stdlib loggers (`uvicorn`, `sqlalchemy`, `httpx`, `langchain`) are all rendered as JSON and run through PII redaction, so the `stage.json` parse stage and the **Stdlib intercept routing** panel work against it directly. This stack scrapes a file, so `PRIMEAGENT_LOG_FILE` is required. If you instead run Primeagent as a container, you can drop the file and scrape its stdout by swapping Alloy's `loki.source.file` target for [`loki.source.docker`](https://grafana.com/docs/alloy/latest/reference/components/loki/loki.source.docker/).

See [Logs and observability](../../../docs/docs/Develop/observability-grafana-loki.mdx) for the full list of environment variables (per-logger overrides, extra PII redaction keys, trace correlation, etc.).

## Run

From this directory:

```bash
# Point Alloy at the directory that holds the file you set in
# PRIMEAGENT_LOG_FILE above. Must be the same directory. Defaults to the
# bundled ./logs (used by the quick smoke test below).
export PRIMEAGENT_LOG_DIR=/absolute/path/to/primeagent/logs

docker compose up -d
```

Then open [http://localhost:3000/d/primeagent-prod-logs](http://localhost:3000/d/primeagent-prod-logs). Default credentials are `admin` / `admin` (override with `GF_ADMIN_USER` and `GF_ADMIN_PASSWORD`).

To stop:

```bash
docker compose down -v
```

### Quick smoke test (no Primeagent required)

To verify the stack end to end without running Primeagent, write a sample record into the bundled `./logs` directory and query Loki directly:

```bash
mkdir -p logs
echo '{"event":"smoke test","level":"info","logger":"primeagent.api.run","timestamp":"2026-06-01T00:00:00Z","service":"primeagent","environment":"production","version":"1.10.0"}' >> logs/primeagent.log

docker compose up -d

# Give Alloy a few seconds to tail the file, then confirm the line reached Loki:
sleep 5
curl -sG 'http://localhost:3100/loki/api/v1/query_range' --data-urlencode 'query={job="primeagent"}' | grep -q "smoke test" && echo "OK: log reached Loki"
```

## What each dashboard panel proves

| Panel | LogQL it runs |
|---|---|
| **PII leak count (must be 0)** | `sum(count_over_time({job="primeagent"} \|~ "sk-do-not-leak\|hunter2\|Bearer xyz" [$__range]))` |
| **Errors with structured tracebacks** | `{job="primeagent", level=~"error\|critical"} \|= "exception" \| json` |
| **Redaction proof** | `{job="primeagent"} \|~ "\\*\\*\\*"` |
| **Stdlib intercept routing** | `{job="primeagent", logger=~"uvicorn.*\|sqlalchemy.*\|httpx.*\|langchain.*"}` |
| **Service / environment / version coverage** | `sum by (service, environment, version) (count_over_time({job="primeagent"}[$__range]))` |
| **Log rate by level** | `sum by (level) (rate({job="primeagent"}[1m]))` |
| **Log rate by logger** | `topk(10, sum by (logger) (rate({job="primeagent"}[1m])))` |

## Notes

- Alloy only promotes `level`, `service`, `environment`, `version`, `logger` to labels. High-cardinality fields (`user_id`, `flow_id`, `trace_id`) stay in the log body — query them with `| json` in LogQL.
- A legacy Promtail config remains at [`promtail/config.yml`](./promtail/config.yml) for reference. Promtail reached end of life on March 2, 2026 and is not started by compose. Grafana documents a [Promtail-to-Alloy conversion](https://grafana.com/docs/alloy/latest/set-up/migrate/from-promtail/).
- If your runtime ships logs through a different transport (Fluent Bit, Vector, OTLP), only the scrape side changes — the dashboard and label schema stay the same.
