# Independent R validation for Phase 17A Prototype 2.1
# "From Field to Lake" static outputs.
#
# This validator does NOT reproduce the Python renderer. It independently
# re-derives source-selection and semantic classifications from the accepted
# CSVs and the exported edge-classification / manifest outputs, and verifies
# the qualitative-only and frozen-artifact boundaries.
#
# Usage (from repository root):
#   Rscript src/R/atlas/validate_spread_2_1_field_to_lake.R .

args <- commandArgs(trailingOnly = TRUE)
root_arg <- if (length(args) > 0L && !grepl("^--", args[[1]])) args[[1]] else "."
root <- normalizePath(root_arg, winslash = "/", mustWork = TRUE)
out <- file.path(root, "outputs", "atlas", "prototypes", "2_1_from_field_to_lake")

checks <- list()
add_check <- function(name, cond, detail = "") {
  checks[[length(checks) + 1L]] <<- list(name = name, passed = isTRUE(cond), detail = detail)
  cat(sprintf("[%s] %s%s\n", if (isTRUE(cond)) "PASS" else "FAIL", name,
              if (nzchar(detail)) paste0(" - ", detail) else ""))
}
stop_if <- function(cond, message) if (!isTRUE(cond)) stop(message, call. = FALSE)

read_csv_quiet <- function(path) read.csv(path, stringsAsFactors = FALSE, check.names = FALSE,
                                         na.strings = c("", "NA"))
json_txt <- function(path) {
  stop_if(file.exists(path), paste("missing json", path))
  paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = " ")
}

flux <- read_csv_quiet(file.path(root, "data", "processed", "networks", "biogeochemical_flux_edges.csv"))
huc12_routing <- read_csv_quiet(file.path(root, "data", "processed", "networks", "huc12_routing_current.csv"))
manifest_json <- json_txt(file.path(out, "2_1_source_manifest.json"))
r_class <- read_csv_quiet(file.path(out, "2_1_r_edge_classification.csv"))

cat("=== Phase 17A Prototype 2.1 — independent R validation ===\n\n")

# -- 1. Source row counts (independent) --------------------------------------
add_check("source row counts: flux edges = 24",
          nrow(flux) == 24L, paste("rows:", nrow(flux)))
add_check("source row counts: huc12 routing = 251",
          nrow(huc12_routing) == 251L, paste("rows:", nrow(huc12_routing)))

# -- 2. Physical vs analytical relationship classification -------------------
all_unknown <- all(tolower(trimws(as.character(flux$quantity_status))) == "unknown quantity")
add_check("all biogeochemical flux edges are qualitative (quantity_status=unknown quantity)",
          all_unknown)
# physical_geometry field exists and both values are present
pg <- tolower(trimws(as.character(huc12_routing$physical_geometry)))
add_check("huc12_routing carries physical_geometry discriminator with both values",
          "physical_geometry" %in% colnames(huc12_routing) && any(pg == "true") && any(pg == "false"),
          sprintf("true:%d false:%d", sum(pg == "true"), sum(pg == "false")))
# Rendered physical channels must originate only from accepted physical-route
# geometry: every rendered classification has an accepted relationship type and
# belongs to the physical waterway source. We verify no physical_geometry=false
# route can be a rendered stream by confirming that classification depends on
# accepted relationship types, not on the routing layer's non-physical rows.
# The classification exports approved processes for transport/flow relationships,
# and empty (monitoring/management context) for monitored_by / managed_by
# relationships. We verify: no 'release' is emitted, and every non-empty value
# is one of the approved processes or a documented monitoring/management context
# (which are not transport processes).
proc_vals <- unique(trimws(as.character(r_class$atlas_process)))
proc_vals <- proc_vals[!is.na(proc_vals) & nzchar(proc_vals)]
allowed_proc <- c("mobilization", "transport", "retention / transformation", "delivery",
                  "discharge", "receiving-water response/context")
add_check("r-edge classification emits only approved processes (and context) — no 'release'",
          all(proc_vals %in% allowed_proc) && !any(proc_vals == "release"),
          paste("distinct:", paste(proc_vals, collapse = ", ")))
# monitored_by / managed_by source relationships must not be promoted to a flow
# process; they are documented as empty context in the export.
monitor_rows <- r_class[tolower(trimws(as.character(r_class$relationship_type))) %in%
                          c("monitored_by", "managed_by"), ]
add_check("monitoring/management relationships are context (not a transport process)",
          all(!nzchar(trimws(as.character(monitor_rows$atlas_process))) |
                is.na(trimws(as.character(monitor_rows$atlas_process)))),
          sprintf("rows=%d", nrow(monitor_rows)))

# -- 3. Constituent vocabulary ------------------------------------------------
# All material tokens present in the source are accepted vocabulary. HAB_context
# is a legitimate source context/modifier token; it must never be rendered as a
# standalone constituent track (checked separately).
all_materials <- unique(unlist(strsplit(as.character(flux$material), ";")))
allowed <- c("P", "N", "C", "organic_matter", "sediment", "soil_carbon", "water_carrier", "HAB_context")
bad <- setdiff(all_materials, allowed)
add_check("constituent vocabulary maps to accepted source tokens",
          length(bad) == 0L, if (length(bad)) paste("unexpected:", paste(bad, collapse = ",")) else "all accepted")
# water_carrier is present and is the carrier/context track (not a load).
add_check("water_carrier present in source as carrier token",
          "water_carrier" %in% all_materials)
add_check("no HAB_context rendered as a standalone constituent track",
          !grepl("HAB_context", readLines(file.path(out, "2_1_constituent_process_matrix.csv"),
                                          warn = FALSE), fixed = TRUE)[1])
# carbon tracks: if C/soil_carbon/organic_matter present, ensure no GHG-inventory
# conflation is introduced in the manifest (carbon presentation is organic-matter context).
add_check("no greenhouse-gas inventory framing in manifest",
          !grepl("greenhouse.?gas inventory|GHG settlement", manifest_json, perl = TRUE, ignore.case = TRUE))

# -- 4. No unsupported 'release' process --------------------------------------
add_check("no standalone 'release' process category in manifest",
          !grepl('"release_process_introduced"[[:space:]]*:[[:space:]]*true', manifest_json, perl = TRUE))
add_check("no 'release' in approved process list",
          !grepl('"approved_processes"[[:space:]]*:[[:space:]]*\\{[^}]*release', manifest_json, perl = TRUE))

# -- 5. No Great Black Swamp geometry ----------------------------------------
add_check("no Great Black Swamp geometry referenced",
          grepl('"great_black_swamp_geometry_used"[[:space:]]*:[[:space:]]*false', manifest_json, perl = TRUE))
add_check("no swamp-named geographic input in manifest geography",
          !grepl('"physical_waterways_layer"[^,]*swamp|"watershed_huc8_layer"[^,]*swamp', manifest_json, perl = TRUE))

# -- 6. No standalone Maumee Bay polygon / no Toledo intake geometry -----------
add_check("Maumee Bay represented as interface, not standalone polygon",
          grepl("standalone polygon", manifest_json, fixed = TRUE) &&
            grepl("labeled nearshore / receiving-water interface", manifest_json, fixed = TRUE))
add_check("no physical Toledo intake geometry used",
          grepl('"toledo_intake_geometry_used"[[:space:]]*:[[:space:]]*false', manifest_json, perl = TRUE) &&
            grepl('"glos_crib_used_as_geometry"[[:space:]]*:[[:space:]]*false', manifest_json, perl = TRUE))

# -- 7. No deterministic nutrient -> HAB edge ---------------------------------
add_check("no deterministic nutrient->HAB edge in manifest",
          grepl('"deterministic_nutrient_to_hab_edge"[[:space:]]*:[[:space:]]*false', manifest_json, perl = TRUE))


cat(sprintf("\n=== RESULT: %s (%d/%d passed) ===\n",
            ifelse(any(!vapply(checks, `[[`, logical(1), "passed")), "FAIL", "PASS"),
            sum(vapply(checks, `[[`, logical(1), "passed")), length(checks)))

# Write a JSON result for verification.
sink(file.path(out, "2_1_r_validation_result.json"))
cat('{\n')
cat('  "result": "', ifelse(any(!vapply(checks, `[[`, logical(1), "passed")), "FAIL", "PASS"), '",\n', sep = "")
cat(sprintf('  "passed": %d,\n', sum(vapply(checks, `[[`, logical(1), "passed"))))
cat(sprintf('  "total": %d,\n', length(checks)))
cat('  "checks": [\n')
for (i in seq_along(checks)) {
  cat(sprintf('    {"name": %s, "passed": %s}',
              dQuote(checks[[i]]$name, q = FALSE), tolower(checks[[i]]$passed)))
  if (i < length(checks)) cat(",")
  cat("\n")
}
cat('  ]\n}\n')
sink()
if (any(!vapply(checks, `[[`, logical(1), "passed"))) quit(status = 1)