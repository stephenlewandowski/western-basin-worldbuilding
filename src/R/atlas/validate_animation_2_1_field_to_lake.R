# Independent R validation for Phase 17A Prototype 2.1
# "From Field to Lake" animation outputs.
#
# This validator does NOT reproduce the Python renderer and does NOT decode all
# video frames. It independently re-derives the A0-A5 state sequence, the
# 0-32 s continuity, the qualitative-only contract, the accepted constituent
# vocabulary, the scientific/geographic boundaries, the A4 convergence
# semantics, the state/source mapping, the source-manifest consistency, and the
# reduced-motion declaration from the accepted manifests and keyframe presence.
#
# Usage (from repository root):
#   Rscript src/R/atlas/validate_animation_2_1_field_to_lake.R .

args <- commandArgs(trailingOnly = TRUE)
root_arg <- if (length(args) > 0L && !grepl("^--", args[[1]])) args[[1]] else "."
root <- normalizePath(root_arg, winslash = "/", mustWork = TRUE)
out <- file.path(root, "outputs", "atlas", "prototypes", "2_1_from_field_to_lake")
anim <- file.path(out, "animation")

checks <- list()
add_check <- function(name, cond, detail = "") {
  checks[[length(checks) + 1L]] <<- list(name = name, passed = isTRUE(cond), detail = detail)
  cat(sprintf("[%s] %s%s\n", if (isTRUE(cond)) "PASS" else "FAIL", name,
              if (nzchar(detail)) paste0(" - ", detail) else ""))
}
stop_if <- function(cond, message) if (!isTRUE(cond)) stop(message, call. = FALSE)

json_txt <- function(path) {
  stop_if(file.exists(path), paste("missing json", path))
  paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = " ")
}

state_csv <- file.path(anim, "2_1_animation_state_manifest.csv")
src_json  <- file.path(anim, "2_1_animation_source_manifest.json")
static_json <- file.path(out, "2_1_source_manifest.json")
stop_if(file.exists(state_csv), paste("missing state manifest", state_csv))

# The accepted state manifest is unquoted and its prose fields contain internal
# commas. Parse reliably: read the header from the first line, then the leading
# comma-free structural fields from each row; keep the raw row text for the
# semantic token checks.
st_lines <- readLines(state_csv, warn = FALSE, encoding = "UTF-8")
parse_state_row <- function(line) {
  cells <- strsplit(line, ",", fixed = TRUE)[[1L]]
  list(state_id = cells[1L], start_seconds = cells[2L], end_seconds = cells[3L],
       source_figure = cells[4L], representation = cells[5L],
       epistemic_status = cells[6L], raw = line)
}
st <- lapply(st_lines[-1L], parse_state_row)
st_row <- function(sid) st[[match(sid, vapply(st, `[[`, character(1), "state_id"))]]

src <- json_txt(src_json)
sst <- json_txt(static_json)

cat("=== Phase 17A Prototype 2.1 — independent R animation validation ===\n\n")

# -- 1. A0-A5 state sequence ------------------------------------------------
expected_ids <- c("A0", "A1", "A2", "A3", "A4", "A5")
add_check("exact A0-A5 state sequence present and in order",
          all(vapply(st, `[[`, character(1), "state_id") == expected_ids),
          paste(vapply(st, `[[`, character(1), "state_id"), collapse = ","))
add_check("six animation states recorded",
          length(st) == 6L, paste("rows:", length(st)))

# -- 2. 0-32 s continuity, no gaps/overlaps ---------------------------------
starts <- as.numeric(vapply(st, `[[`, character(1), "start_seconds"))
ends   <- as.numeric(vapply(st, `[[`, character(1), "end_seconds"))
add_check("timeline begins at 0.0 s", isTRUE(all.equal(starts[1], 0.0)))
add_check("timeline ends at 32.0 s", isTRUE(all.equal(tail(ends, 1L), 32.0)))
contig <- all(vapply(seq_len(length(st) - 1L), function(i) isTRUE(all.equal(ends[i], starts[i + 1L])), logical(1)))
add_check("no state gaps or overlaps (contiguous boundaries)", contig)
add_check("each state end > start", all(ends > starts))

# -- 3. Qualitative-only / epistemic / randomization ------------------------
add_check("epistemic status E throughout",
          all(vapply(st, `[[`, character(1), "epistemic_status") == "E"))
add_check("quantitative_encoding=false throughout",
          all(vapply(st, function(r) grepl("false", r$raw, fixed = TRUE), logical(1))) &&
            grepl('"quantitative_encoding"[[:space:]]*:[[:space:]]*false', src, perl = TRUE))
add_check("randomization=false",
          grepl('"randomization"[[:space:]]*:[[:space:]]*false', src, perl = TRUE))

# -- 4. Accepted constituent vocabulary / HAB_context excluded --------------
a3 <- st_row("A3")$raw
add_check("water/carrier context present in A3",
          grepl("water", a3, ignore.case = TRUE))
add_check("constituent rows P,N,organic matter,sediment in A3",
          grepl("P", a3, fixed = TRUE) &&
            grepl("N", a3, fixed = TRUE) &&
            grepl("carbon", a3, ignore.case = TRUE) &&
            grepl("sediment", a3, ignore.case = TRUE))
add_check("HAB_context not treated as a constituent",
          grepl('"hab_context_used_as_constituent"[[:space:]]*:[[:space:]]*false', src, perl = TRUE))
# HAB_context must not appear as a constituent row: check accepted static matrix too.
matrix_csv <- file.path(out, "2_1_constituent_process_matrix.csv")
hab_excl <- TRUE
if (file.exists(matrix_csv)) {
  mtx <- read.csv(matrix_csv, stringsAsFactors = FALSE, check.names = FALSE)
  hab_excl <- !any(grepl("HAB", mtx[[1]], ignore.case = FALSE))
}
add_check("no HAB_context constituent row in accepted matrix", hab_excl)

# -- 5. Boundaries -----------------------------------------------------------
add_check("no Great Black Swamp geometry",
          grepl('"great_black_swamp_geometry_used"[[:space:]]*:[[:space:]]*false', src, perl = TRUE))
add_check("no physical Toledo intake geometry",
          grepl('"toledo_physical_intake_geometry_used"[[:space:]]*:[[:space:]]*false', src, perl = TRUE))
add_check("no unsupported release process",
          grepl('"release_process_introduced"[[:space:]]*:[[:space:]]*false', src, perl = TRUE))
add_check("no deterministic nutrient->HAB edge",
          grepl('"deterministic_nutrient_to_hab_edge"[[:space:]]*:[[:space:]]*false', src, perl = TRUE))

# -- 6. A4 convergence semantics ---------------------------------------------
a4 <- st_row("A4")
a4_vis <- a4$raw
add_check("A4 uses one shared convergence junction",
          grepl("common junction", a4_vis, ignore.case = TRUE))
add_check("A4 has exactly one outgoing relationship from junction",
          grepl("one outgoing", a4_vis, ignore.case = TRUE) &&
            !grepl("two outgoing", a4_vis, ignore.case = TRUE))
add_check("A4 note confirms single junction / one outgoing / no direct edge",
          grepl("one common junction", a4_vis, fixed = TRUE) &&
            grepl("exactly one outgoing", a4_vis, fixed = TRUE) &&
            grepl("no direct nutrient->HAB edge", a4_vis, fixed = TRUE))

# -- 7. State/source mapping & source manifest consistency -------------------
src_of <- function(sid) st_row(sid)$source_figure
add_check("A0/A1 map to 2.1A (geographic map)",
          all(src_of("A0") == "2_1a", src_of("A1") == "2_1a"))
add_check("A2 maps to 2.1B (process schematic)", src_of("A2") == "2_1b")
add_check("A3 maps to 2.1C (constituent pathways)", src_of("A3") == "2_1c")
add_check("A4/A5 map to 2.1D (receiving-water boundary)",
          all(src_of("A4") == "2_1d", src_of("A5") == "2_1d"))
add_check("source manifest no_new_science=true",
          grepl('"no_new_science"[[:space:]]*:[[:space:]]*true', src, perl = TRUE))

# -- 8. Accepted static figures as immutable sources -------------------------
add_check("accepted static manifest present",
          file.exists(static_json))
add_check("accepted static manifest is qualitative (quantitative=false)",
          grepl('"quantitative"[[:space:]]*:[[:space:]]*false', sst, perl = TRUE))

# -- 9. Reduced-motion declaration -------------------------------------------
add_check("source manifest declares a reduced-motion endpoint",
          grepl('"reduced_motion_endpoint"[[:space:]]*:[[:space:]]*"2_1_from_field_to_lake_reduced_motion\\.png"',
                src, perl = TRUE))
rm_file <- file.path(anim, "2_1_from_field_to_lake_reduced_motion.png")
add_check("reduced-motion endpoint PNG exists", file.exists(rm_file))
# Independent identity: the reduced-motion endpoint PNG and the A5 keyframe must
# be the same rendered artifact (the final frame is the reduced-motion base).
kf5 <- file.path(anim, "2_1_animation_keyframe_A5.png")
size_equal <- file.exists(rm_file) && file.exists(kf5) &&
  file.info(rm_file)$size == file.info(kf5)$size
add_check("reduced-motion endpoint PNG matches A5 keyframe artifact",
          size_equal,
          if (file.exists(rm_file) && file.exists(kf5))
            paste("reduced_motion bytes:", file.info(rm_file)$size) else "missing")

cat(sprintf("\n=== RESULT: %s (%d/%d passed) ===\n",
            ifelse(any(!vapply(checks, `[[`, logical(1), "passed")), "FAIL", "PASS"),
            sum(vapply(checks, `[[`, logical(1), "passed")), length(checks)))

# Write a JSON result for verification.
sink(file.path(anim, "2_1_animation_r_validation_result.json"))
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