# Phase 3A Freeze Hash Portability

The Phase 3A freeze manifest records the Windows CRLF working-tree hash for
`data/processed/networks/energy_system_nodes.csv`:

`96eac0aa0e71c9474f25601be5eae1ffed0a57dc547b8032610b9c1ed5847160`

The accepted Git-stored LF representation hashes to
`4036d3443624a47091b094032de7e3438f3ddfc9233a26926511860b085533f2`.
The CSV is semantically identical: 18 rows, 17 columns, and zero cell
changes. No later commit modified the file.

`src/python/systems/freeze_hash.py` now accepts a raw manifest match first and,
for explicitly text artifacts only, proves LF/CRLF equivalence against the Git
blob at `HEAD`. Binary artifacts remain raw-byte strict. The focused
`test_freeze_hash_portability.py` test verifies equivalent LF and CRLF content
passes while a one-cell CSV mutation fails.
