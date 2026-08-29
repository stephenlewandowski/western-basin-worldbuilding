args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) > 0) args[[1]] else "."
nodes <- read.csv(file.path(root, "data", "processed", "networks", "water_system_nodes.csv"), stringsAsFactors = FALSE)
edges <- read.csv(file.path(root, "data", "processed", "networks", "water_system_edges.csv"), stringsAsFactors = FALSE)
stopifnot(all(edges$from_id %in% nodes$feature_id))
stopifnot(all(edges$to_id %in% nodes$feature_id))
fictional <- nodes[nodes$reality_status == "fictional", ]
stopifnot(all(is.na(fictional$longitude)), all(is.na(fictional$latitude)))
stopifnot(all(edges$relationship_basis %in% c("observed", "engineering_dependency", "scientific_inference", "scenario_assumption")))
cat("R validation passed:", nrow(nodes), "nodes;", nrow(edges), "edges\n")
