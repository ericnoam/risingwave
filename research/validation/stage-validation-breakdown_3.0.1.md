# Avro schema validation — `stage-` topics breakdown (3.0.1)

Generated from `avro-validator --all` output captured against the 3.0.1 branch (`research/validation_3.0.1.txt`), filtered to topics starting with `stage-`.

- Source (full): [`validation_3.0.1.txt`](../validation_3.0.1.txt)
- Source (filtered): [`stage-only-validation-errors_3.0.1.txt`](stage-only-validation-errors_3.0.1.txt)
- Matrix: [`stage-validation-matrix_3.0.1.csv`](stage-validation-matrix_3.0.1.csv)
- **18790 stage topics** retained; 955 non-`stage-` topics removed from the original report (19745 total subjects in the source file).
- Of the 18790 stage topics, 18391 validate OK and 399 fail RisingWave's Avro decode (these decode failures are separate from — and mostly unrelated to — the structural checks below).

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

`0` means the topic matched none of the structural checks (typically a `-key` subject, a primitive schema, or a schema that failed to decode before checks could run).

| # categories | topics |
|---|---|
| 0 | 12139 |
| 1 | 2217 |
| 2 | 1904 |
| 3 | 2518 |
| 4 | 12 |

## 🔴 Blocking — `union-of-named-types` (19 topics)

The only category RisingWave rejects. These will **fail to ingest** until the union is flattened or its variants wrapped in a record.

| topic | named variants | also flagged |
|---|---|---|
| stage-malta.pub.frontend-frontend-event-value | 33 | logical-type, field-default, reference-use |
| stage-italy.pub.frontend-frontend-event-value | 32 | logical-type, field-default, reference-use |
| stage-mgm-nl.pub.frontend-frontend-event-value | 32 | logical-type, field-default, reference-use |
| stage-spain.pub.frontend-frontend-event-value | 32 | logical-type, field-default, reference-use |
| stage-nl.pub.frontend-frontend-event-value | 30 | logical-type, field-default, reference-use |
| stage-malta.pub.cat-player-event-value | 25 | logical-type, reference-use |
| stage-malta.pub.personalization-player-event-value | 25 | logical-type, reference-use |
| stage-malta.pub.playerevent-player-event-value | 25 | logical-type, reference-use |
| stage-uk.pub.frontend-frontend-event-value | 23 | logical-type, field-default, reference-use |
| stage-b2b.pub.frontend-frontend-event-value | 20 | logical-type, field-default, reference-use |
| stage-vibet.pub.frontend-frontend-event-value | 18 | logical-type, field-default, reference-use |
| stage-malta.pub.retention-journey-config-event-value | 14 | field-default, reference-use |
| stage-b2b-jv8.pub.frontend-frontend-event-value | 10 | logical-type, reference-use |
| stage-malta.pub.retention-daily-batch-process-completed-value | 5 | reference-use |
| stage-malta.pub.retention-scheduled-campaign-approval-value | 5 | reference-use |
| stage-malta.pub.retention-scheduled-campaign-sendout-value | 5 | reference-use |
| stage-malta.pub.retention-triggered-campaign-approval-value | 5 | reference-use |
| stage-malta.pub.retention-triggered-campaign-sendout-value | 5 | reference-use |
| stage-malta.pub.retention-upsert-customer-callback-value | 2 | — |

## 🟡 single-variant-union (18 topics)

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

- `stage-b2b.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.forcedlimitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.limitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.userlimitevent`
- `stage-italy.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.forcedlimitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.limitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.userlimitevent`
- `stage-malta.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.forcedlimitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.limitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.userlimitevent`
- `stage-malta.pub.respgaming-limit-override-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.limitoverrideevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.marketlimitoverrideevent`
- `stage-mgm-nl.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.forcedlimitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.limitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.userlimitevent`
- `stage-mgm-nl.pub.respgaming-limit-override-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.limitoverrideevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.marketlimitoverrideevent`
- `stage-nl.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.forcedlimitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.limitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.userlimitevent`
- `stage-spain.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.forcedlimitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.limitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.userlimitevent`
- `stage-uk.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.forcedlimitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.limitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.userlimitevent`
- `stage-vibet.pub.respgaming-limit-event-value: EventType: com.gearsofleo.platform.core.responsiblegaming.limits.api.event.forcedlimitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.limitevent, com.gearsofleo.platform.core.responsiblegaming.limits.api.event.userlimitevent`

## 🟡 aliases (4 topics)

- `stage-ist.pub.gaming-bet-event-value: gameSessionUid [sessionUid]`
- `stage-malta.pub.gaming-bet-event-value: gameSessionUid [sessionUid]`
- `stage-mgm-nl.pub.gaming-bet-event-value: gameSessionUid [sessionUid]`
- `stage-spain.pub.gaming-bet-event-value: gameSessionUid [sessionUid]`

## ⚪ Inventory categories (informational, not failures)

| Category | distinct stage topics |
|---|---|
| `logical-type` | 4577 |
| `field-default` | 4656 |
| `reference-use` | 4343 |

These cover nearly every topic and are review inventories, not incompatibilities. See the CSV for per-topic counts.

## Case study: what `union-of-named-types` actually looks like, and how to fix it

Pulled live from the schema registry for inspection: [`stage-malta.pub.frontend-frontend-event.avsc`](stage-malta.pub.frontend-frontend-event.avsc) (subject `stage-malta.pub.frontend-frontend-event-value`, the top row of the blocking table above).

Its field structure:

```
FrontendEvent (record)
  channel:   string
  eventType: string
  event:     union of 33 branches, all record   <- the violation
```

One field, `event`, is typed as a union holding 33 different named record types directly (`SessionEnded`, `DepositApproved`, `PlayerBalance`, `LiveCasinoDynamicData`, …) — a "this message is one of 33 kinds of event" payload field. RisingWave can only map a union to a single column type, so a union with ≥2 named branches has no column it can become; that's the whole reason `union-of-named-types` fails to ingest. It has nothing to do with where the 33 record types are defined (Avro has no cross-schema `$ref` — a named type is always defined once in the document and reused by name after) — it's purely about how many named types sit inside that one union.

The schema already carries `eventType: string` as a discriminator saying which of the 33 is present; the payload just wasn't split accordingly.

**The working pattern already exists elsewhere in this same registry.** `stage-malta.pub.persona-player-value` (the top single-variant-union entry) models an identical "one of N event kinds" shape, but as N sibling nullable fields instead of one N-way union:

```
PersonaPlayer (record)
  type:                        enum (discriminator)
  playerCreatedEvent:          [null, record]
  playerStateChangedEvent:     [null, record]
  playerLockedEvent:           [null, record]
  ... (12 fields total, each [null, <record>])
```

Every message sets exactly one of the 12 fields and leaves the other 11 `null`. This is Avro's idiom for a tagged union — Avro has no native `oneof` like Protobuf, where the wire format only encodes the field that's actually set; here, every message carries all 12 (soon to be 33, in `frontend-frontend-event`'s case) field slots, with all-but-one `null`. The cost is small (a `[null, X]` union costs one index byte on the wire when null, and Avro's JSON encoding just writes literal `null`), and it's exactly what this registry already does everywhere else this shape occurs.

**The fix for `frontend-frontend-event`:** split the 33-branch `event` union into 33 sibling nullable fields (`sessionEnded: [null, SessionEnded]`, `depositApproved: [null, DepositApproved]`, …), matching `persona-player`'s existing pattern. Producers already know which one to populate — they emit `eventType` today — so this is a schema/serialization change, not a logic change.

