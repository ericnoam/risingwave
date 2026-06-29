# Avro schema validation — `stage-` topics breakdown

Generated from `avro-validator` output, filtered to topics starting with `stage-`.

- Source (filtered): [`stage-only-validation-errors.txt`](stage-only-validation-errors.txt)
- Matrix: [`stage-validation-matrix.csv`](stage-validation-matrix.csv)
- **6612 stage topics** retained; 245 non-`stage-` topics removed from the original report.

## Category meanings

| Category | Severity | Meaning |
|---|---|---|
| `union-of-named-types` | 🔴 Blocking | Union with ≥2 named types (record/enum/fixed). RisingWave rejects these (issue 17632) — **fails to ingest**. |
| `single-variant-union` | 🟡 Advisory | One-element union; usually a leftover-null union, changes nullability. |
| `namespace-significant` | 🟡 Advisory | A simple type name reused under multiple namespaces — namespace is load-bearing. |
| `aliases` | 🟡 Advisory | Type/field declares Avro `aliases`; RisingWave matches by name and ignores them. |
| `logical-type` | ⚪ Inventory | Every logical type, shown over its physical type (e.g. `timestamp-micros (on long)`). |
| `field-default` | ⚪ Inventory | Fields with a non-null `default`. |
| `reference-use` | ⚪ Inventory | Every use of a named-type reference. |

## Categories per topic

| # categories | topics |
|---|---|
| 1 | 2208 |
| 2 | 1896 |
| 3 | 2497 |
| 4 | 11 |

## 🔴 Blocking — `union-of-named-types` (19 topics)

The only category RisingWave rejects. These will **fail to ingest** until the union is flattened or its variants wrapped in a record.

| topic | named variants | also flagged |
|---|---|---|
| stage-italy.pub.frontend-frontend-event-value | 32 | field-default, logical-type, reference-use |
| stage-malta.pub.frontend-frontend-event-value | 32 | field-default, logical-type, reference-use |
| stage-mgm-nl.pub.frontend-frontend-event-value | 32 | field-default, logical-type, reference-use |
| stage-spain.pub.frontend-frontend-event-value | 32 | field-default, logical-type, reference-use |
| stage-nl.pub.frontend-frontend-event-value | 30 | field-default, logical-type, reference-use |
| stage-malta.pub.cat-player-event-value | 25 | logical-type, reference-use |
| stage-malta.pub.personalization-player-event-value | 25 | logical-type, reference-use |
| stage-malta.pub.playerevent-player-event-value | 25 | logical-type, reference-use |
| stage-uk.pub.frontend-frontend-event-value | 23 | field-default, logical-type, reference-use |
| stage-b2b.pub.frontend-frontend-event-value | 20 | field-default, logical-type, reference-use |
| stage-vibet.pub.frontend-frontend-event-value | 18 | field-default, logical-type, reference-use |
| stage-malta.pub.retention-journey-config-event-value | 14 | field-default, reference-use |
| stage-b2b-jv8.pub.frontend-frontend-event-value | 10 | logical-type, reference-use |
| stage-malta.pub.retention-daily-batch-process-completed-value | 5 | reference-use |
| stage-malta.pub.retention-scheduled-campaign-approval-value | 5 | reference-use |
| stage-malta.pub.retention-scheduled-campaign-sendout-value | 5 | reference-use |
| stage-malta.pub.retention-triggered-campaign-approval-value | 5 | reference-use |
| stage-malta.pub.retention-triggered-campaign-sendout-value | 5 | reference-use |
| stage-malta.pub.retention-upsert-customer-callback-value | 2 | — |

## 🟡 single-variant-union (18 topics)

Most are `persona-player` with a one-element `[…GenderAvro]` union; the rest are `[string]` singletons.

- `stage-b2b.pub.persona-player-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-ist.pub.persona-player-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-italy.prv.respgaming-regulatory-aams-player.persona-player-dlt-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-italy.prv.respgaming-regulatory-aams-player.persona-player-retry-0-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-italy.prv.respgaming-regulatory-aams-player.persona-player-retry-1-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-italy.prv.respgaming-regulatory-aams-player.persona-player-retry-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-italy.pub.persona-player-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-malta.pub.persona-player-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-malta.pub.respgaming-sga-player-blocked-event-value: [string]`
- `stage-malta.pub.sportsbook-event.kambi-dw.betmgm.reward-templates-value: [string]`
- `stage-malta.pub.sportsbook-event.kambi-dw.betuk.reward-templates-value: [string]`
- `stage-malta.pub.sportsbook-event.kambi-dw.expekt.reward-templates-value: [string]`
- `stage-malta.pub.sportsbook-event.kambi-dw.leo.reward-templates-value: [string]`
- `stage-mgm-nl.pub.persona-player-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-nl.pub.persona-player-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-spain.pub.persona-player-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-uk.pub.persona-player-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`
- `stage-vibet.pub.persona-player-value: [com.gearsofleo.platform.core.player.api.avro.GenderAvro]`

## 🟡 namespace-significant (10 topics)

All `respgaming-limit*-event`: `EventType` defined under multiple namespaces.

- `stage-b2b.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.f …`
- `stage-italy.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event …`
- `stage-malta.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event …`
- `stage-malta.pub.respgaming-limit-override-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits. …`
- `stage-mgm-nl.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.even …`
- `stage-mgm-nl.pub.respgaming-limit-override-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits …`
- `stage-nl.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.fo …`
- `stage-spain.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event …`
- `stage-uk.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.fo …`
- `stage-vibet.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event …`

## 🟡 aliases (3 topics)

`gaming-bet-event`: field `gameSessionUid` aliased as `sessionUid`.

- `stage-malta.pub.gaming-bet-event-value: gameSessionUid [sessionUid]`
- `stage-mgm-nl.pub.gaming-bet-event-value: gameSessionUid [sessionUid]`
- `stage-spain.pub.gaming-bet-event-value: gameSessionUid [sessionUid]`

## ⚪ Inventory categories (informational, not failures)

| Category | distinct stage topics |
|---|---|
| `logical-type` | 4548 |
| `field-default` | 4625 |
| `reference-use` | 4312 |

These cover nearly every topic and are review inventories, not incompatibilities. See the CSV for per-topic counts.
