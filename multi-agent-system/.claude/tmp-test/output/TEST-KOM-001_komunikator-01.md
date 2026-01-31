# TEST-KOM-001 - Smoke test: komunikator output
Agent: komunikator-01
Role: komunikator
Timestamp: 2026-01-26T19:00:41.557868

**Task ID:** TEST-KOM-001  
**Title:** Smoke test: komunikator output  

**Brief plan**
1. Define the minimal “komunikator” output contract (fields, ordering, required/optional).
2. Draft a smoke test input and the expected output payload.
3. Execute a one-step validation (golden output compare) in CI or locally.
4. Record results and note any deviations.

**Mock TZs (tiny fictive scope)**
- `TZ_A`: `Europe/Warsaw` (CET/CEST)  
- `TZ_B`: `Europe/Prague` (CET/CEST)  
- `TZ_C`: `UTC`  

**Example mock data**
```json
{
  "scope": "tiny-fictive",
  "timezones": ["TZ_A", "TZ_B", "TZ_C"],
  "expected_output_format": "plain-text"
}
```**Task ID:** TEST-KOM-001  
**Title:** Smoke test: komunikator output  

**Brief plan**
1. Define the minimal “komunikator” output contract (fields, ordering, required/optional).
2. Draft a smoke test input and the expected output payload.
3. Execute a one-step validation (golden output compare) in CI or locally.
4. Record results and note any deviations.

**Mock TZs (tiny fictive scope)**
- `TZ_A`: `Europe/Warsaw` (CET/CEST)  
- `TZ_B`: `Europe/Prague` (CET/CEST)  
- `TZ_C`: `UTC`  

**Example mock data**
```json
{
  "scope": "tiny-fictive",
  "timezones": ["TZ_A", "TZ_B", "TZ_C"],
  "expected_output_format": "plain-text"
}
```
