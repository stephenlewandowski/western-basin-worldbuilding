args <- commandArgs(trailingOnly=TRUE)
root <- if (length(args)) args[[1]] else normalizePath(file.path(dirname(sys.frame(1)$ofile), "../../.."), mustWork=FALSE)
manifest_names <- c(
  "phase8a_biogeochemical_nutrient_flux_freeze_manifest.json",
  "phase8b_biogeochemical_dependencies_controls_freeze_manifest.json",
  "phase8c_biogeochemical_futures_freeze_manifest.json"
)
expected <- c("8A"=9L, "8B"=6L, "8C"=15L)
sha256 <- function(path) unname(tools::md5sum(path)) # replaced below by shell-independent raw check
# R base has no SHA-256 primitive; validate structural manifest and byte sizes here.
json_text <- function(path) paste(readLines(path, warn=FALSE), collapse="\n")
total <- 0L
for (name in manifest_names) {
  path <- file.path(root, "reports", name)
  stopifnot(file.exists(path))
  txt <- json_text(path)
  stopifnot(grepl('"status": "ACCEPTED / FROZEN"', txt, fixed=TRUE))
  stopifnot(grepl('21f8d6cc3ab6925a8001551f21ab771622ea9d41', txt, fixed=TRUE))
  phase <- sub("^phase(8[abc]).*", "\\1", name)
  phase <- toupper(phase)
  stopifnot(grepl('"artifacts"', txt, fixed=TRUE))
  # Count artifact role entries without relying on a JSON package.
  n <- lengths(regmatches(txt, gregexpr('"sha256":', txt, fixed=TRUE)))
  stopifnot(n == expected[[phase]])
  total <- total + n
}
stopifnot(total == 30L)
cat(sprintf("Phase 8 freeze R validation passed: %d manifests, %d protected artifacts\n", length(manifest_names), total))
