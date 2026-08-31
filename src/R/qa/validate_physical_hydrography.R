args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) normalizePath(args[[1]], mustWork = TRUE) else normalizePath(".", mustWork = TRUE)

reconciliation <- read.csv(file.path(root, "reports", "wbd_connector_reconciliation.csv"), stringsAsFactors = FALSE)
transitions <- read.csv(file.path(root, "outputs", "qa", "data", "3dhp_huc12_transitions.csv"), stringsAsFactors = FALSE)
routing <- read.csv(file.path(root, "outputs", "qa", "data", "huc12_authoritative_routing.csv"), stringsAsFactors = FALSE)

allowed <- c(
  "REPLACED_PHYSICAL",
  "REPLACED_AUTHORITATIVE_CONNECTOR",
  "ALREADY_REDUNDANT",
  "UNRESOLVED",
  "INVALID_BASELINE_INFERENCE"
)

stopifnot(nrow(reconciliation) == 251)
stopifnot(length(unique(reconciliation$old_connector_id)) == 251)
stopifnot(all(reconciliation$qa_status %in% allowed))
stopifnot(all(reconciliation$from_huc12 != reconciliation$to_huc12))
stopifnot(length(unique(transitions$transition_id)) == nrow(transitions))
stopifnot(all(transitions$from_huc12 != transitions$to_huc12))
stopifnot(all(transitions$transition_class %in% c("physical_hydrography", "authoritative_network_connector")))
stopifnot(nrow(routing) == 252)
stopifnot(length(unique(routing$huc12)) == 252)

counts <- table(factor(reconciliation$qa_status, levels = allowed))
names(counts) <- c("Physical", "Official connector", "Redundant", "Unresolved", "Invalid")
png_path <- file.path(root, "outputs", "qa", "physical_hydrography_R_validation.png")
png(png_path, width = 1600, height = 1000, res = 160)
par(mar = c(9, 5, 4, 2) + 0.1)
bars <- barplot(
  counts,
  col = c("#2166ac", "#666666", "#159c9c", "#b2182b", "#7a0177"),
  las = 2,
  ylab = "Released inferred connectors",
  main = "Independent R Check - Physical Hydrography Reconciliation",
  ylim = c(0, max(counts) * 1.15)
)
text(bars, counts, labels = counts, pos = 3)
abline(h = pretty(c(0, max(counts))), col = "#dddddd", lty = 3)
box()
dev.off()

cat("PASS: R independently validated 251 connector outcomes\n")
cat(sprintf("PASS: %d native cross-HUC transitions and 252 HUC routing rows\n", nrow(transitions)))
cat(sprintf("PASS: rendered %s\n", png_path))
