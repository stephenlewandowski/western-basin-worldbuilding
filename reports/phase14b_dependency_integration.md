# Phase 14B Dependency Integration

Status: additive Atlas-facing dependency crosswalk; local source tables are read-only inputs.

Dependency crosswalk rows: **761** across **11** canonical dependency artifacts.

| Evidence class | Rows |
|---|---:|
| `CONTEXT_REUSED` | 52 |
| `INFERRED` | 515 |
| `OBSERVED_DOCUMENTED` | 194 |

## Population high-inference handling

- Total population dependency rows: **520**
- Inferred: **468**
- Reused context: **52**
- Inferred and reused-context rows retain source evidence class, source phase/artifact, inference basis, native spatial scale, directionality, uncertainty, and visualization/use flags.
- Inferred rows support visualization and qualitative reasoning; stress-test propagation is qualitative-only; quantitative aggregation is prohibited.
- No numeric confidence score was added.

## Endpoint and lineage boundary

- Phase 13B endpoint-role occurrences: **36**; roles: ecological entity=8, generalized external interface=7, geographic unit=4, institutional actor=5, monitoring/surveillance interface=6, physical asset=1, population/settlement entity=5.
- The 0 exact / 34 system-level / 2 retained conceptual Phase 14A endpoint result is preserved. EXT-OCCUPATIONAL-CONTACT and EXT-INFRASTRUCTURE remain generalized external interfaces.
- Every dependency row retains its local relationship ID, source phase, source artifact, and local endpoint IDs.

## Joinability

- System-pair matrix rows: **78**.
- The matrix is an interoperability matrix, not a risk matrix; it contains no summed connectivity score or composite risk score.
