# Phase 14A Relationship Taxonomy Inventory

Inventory rows: **367** local field/term/artifact observations.

## Candidate high-level classes

- ecological relationship: **44**
- energy flow: **12**
- exposure pathway: **21**
- governance / authority: **30**
- high-level interface / association: **14**
- information / observation: **57**
- material flow: **15**
- operational dependency: **66**
- physical flow: **13**
- population / mobility interface: **7**
- scenario influence: **44**
- unclassified candidate: **44**

## Interpretation

This is an inventory, not Phase 14B normalization. `dependency`, `interface`, `contextual`, `affects`, and similar generic terms are ambiguous without their local evidence basis and scale. Observation/surveillance edges are not physical or causal edges; governance/authority edges do not imply operational control; ecological and exposure interfaces are not disease or risk claims; and scenario relations are not factual observations or forecasts.

## Energy normalization seam

Energy uses distinct local terms such as `electricity`, `fuel`, `cooling_water`, `thermal_dependency`, `storage_support`, `communications`, `generation_grid_interface`, and `grid_serves_load`. The Phase 3B table also uses `to_system=water_or_materials` while four rows target `ENE-LOAD-*` nodes. Phase 14B must retain endpoint role, local dependency type, source basis, direction, and native scale before proposing a join class; 14A does not rewrite these values.
