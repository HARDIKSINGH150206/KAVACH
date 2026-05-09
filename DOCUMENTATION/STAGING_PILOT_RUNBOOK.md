# KAVACH Staging and Pilot Runbook

This runbook defines the minimum checks required to promote KAVACH from local/staging to pilot rollout.

## 1) Pre-Flight

Run from repo root:

```bash
make profile-pilot
```

In another terminal:

```bash
make smoke-check
```

## 2) Gate Checks

Run the automated pilot gate:

```bash
make pilot-gate
```

This gate currently verifies:
- readiness strict pass
- adversarial SMS threshold pass
- backend tests pass
- main frontend lint/build pass
- legacy frontend build pass
- smoke check pass

## 3) Manual Validation

1. Open `http://localhost:5175` and launch dashboard.
2. Confirm backend state badge is visible and updates.
3. Trigger safe/high/critical scenarios and confirm fusion output changes.
4. Verify no blocking errors in browser console.

## 4) Pilot Promotion Criteria

Promote to pilot only when all are true:

1. `make pilot-gate` exits with code `0`.
2. API health endpoint remains stable for 30 minutes under expected traffic.
3. No critical runtime errors in backend logs.
4. Dashboard remains connected/recoverable during backend restart.

## 5) Rollback

If any promotion check fails:

1. Stop pilot profile:
```bash
make stop
```
2. Restart in demo profile:
```bash
make profile-demo
```
3. Capture logs:
```bash
tail -n 300 logs/threat_events.jsonl
```
4. Create issue with failure snapshot and gate output JSON.
