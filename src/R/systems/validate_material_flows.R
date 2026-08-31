# Independent base-R validation of Phase 2B materials-flow tables.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- normalizePath(sub("^--file=", "", file_arg), winslash = "/")
root <- normalizePath(file.path(dirname(script_path), "../../.."), winslash = "/")

nodes <- read.csv(file.path(root, "data/processed/networks/materials_system_nodes.csv"), stringsAsFactors = FALSE, na.strings = NULL)
edges <- read.csv(file.path(root, "data/processed/networks/materials_system_edges.csv"), stringsAsFactors = FALSE, na.strings = NULL)
sources <- read.csv(file.path(root, "data/processed/networks/materials_system_sources.csv"), stringsAsFactors = FALSE, na.strings = NULL)

stopifnot(nrow(nodes) >= 25L, nrow(edges) >= 26L, nrow(sources) >= 14L)
stopifnot(!anyDuplicated(nodes$node_id), !anyDuplicated(edges$edge_id), !anyDuplicated(sources$source_id))
stopifnot(all(edges$from_id %in% nodes$node_id), all(edges$to_id %in% nodes$node_id))
stopifnot(all(nodes$source_id %in% sources$source_id), all(edges$source_id %in% sources$source_id))
relationship_key <- paste(edges$from_id, edges$to_id, edges$material, edges$flow_type, sep = "|")
stopifnot(!anyDuplicated(relationship_key))
stopifnot(all(nzchar(edges$relationship_basis)), all(nzchar(edges$reality_status)),
          all(nzchar(edges$canon_status)), all(nzchar(edges$confidence)), all(nzchar(edges$source_id)))
core_nodes <- nodes[!grepl("^EXP-", nodes$node_id), ]
core_edges <- edges[!grepl("^EXP-", edges$edge_id), ]
stopifnot(nrow(core_nodes) == 25L, nrow(core_edges) == 26L)
stopifnot(identical(sort(unique(core_nodes$material_system)), c("beryllium", "carbonate", "shared")))
stopifnot(all(core_nodes$reality_status == "real"), all(core_edges$reality_status == "real"))
stopifnot(all(nodes$canon_status %in% c("verified", "inferred")), all(edges$canon_status %in% c("verified", "inferred")))
stopifnot(all(core_nodes$scenario_year == "2026"))

elmore <- nodes[nodes$node_id == "BER-PROC-ELMORE", ]
stopifnot(nrow(elmore) == 1L, elmore$supply_chain_role == "advanced_processing", elmore$local_resource == "false")
luckey <- nodes[nodes$node_id == "BER-LEG-LUCKEY", ]
stopifnot(nrow(luckey) == 1L, luckey$supply_chain_role == "legacy_cleanup")
cfs <- edges[edges$edge_id == "BER-E08", ]
stopifnot(nrow(cfs) == 1L, cfs$relationship_basis == "documented_supply_relationship", cfs$relationship_date == "2025-10-31")
kairos <- edges[edges$edge_id == "BER-E09", ]
stopifnot(nrow(kairos) == 1L, grepl("unresolved", kairos$current_status, fixed = TRUE))
stopifnot(!any(c("quantity", "tonnage", "volume", "capacity", "route_geometry", "transport_mode") %in% names(edges)))

figure_path <- file.path(root, "outputs/figures/material_flows_R_validation.png")
png(figure_path, width = 1800, height = 1050, res = 150)
par(mfrow = c(1, 2), mar = c(8, 4, 4, 1), bg = "#f7f4ec")
barplot(table(nodes$material_system), col = c("#6d28d9", "#c99632", "#64748b"), las = 2,
        main = "Phase 2B nodes", ylab = "Count")
barplot(table(edges$relationship_basis), col = "#486581", las = 2,
        main = "Qualified relationships", ylab = "Count", cex.names = 0.75)
mtext("Independent R validation — PASS", outer = TRUE, line = -2, font = 2, col = "#17324d")
dev.off()

cat(sprintf("PASS: %d nodes; %d edges; %d sources; Elmore processing/non-extraction and CFS qualification verified.\n",
            nrow(nodes), nrow(edges), nrow(sources)))
