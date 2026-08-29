args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) > 0) args[[1]] else "."
sites <- read.csv(file.path(root, "outputs", "tables", "materials_sites_render_data.csv"), stringsAsFactors = FALSE)
carbonate <- read.csv(file.path(root, "outputs", "tables", "materials_carbonate_render_data.csv"), stringsAsFactors = FALSE)

required <- c("resource_class", "supply_chain_role", "local_resource", "reality_status",
              "canon_status", "source_name", "source_url_or_identifier", "retrieved_date",
              "confidence", "notes")
stopifnot(all(required %in% names(sites)))
stopifnot(nrow(sites) == 5, nrow(carbonate) > 100)
stopifnot(all(sites$reality_status == "real"), all(sites$canon_status == "verified"))
stopifnot(all(sites$longitude >= -83.95 & sites$longitude <= -82.72))
stopifnot(all(sites$latitude >= 41.12 & sites$latitude <= 41.82))

elmore <- sites[grepl("Elmore", sites$feature_name), ]
luckey <- sites[grepl("Luckey", sites$feature_name), ]
stopifnot(nrow(elmore) == 1, elmore$supply_chain_role == "advanced_processing",
          tolower(as.character(elmore$local_resource)) == "false")
stopifnot(nrow(luckey) == 1, luckey$supply_chain_role == "legacy_cleanup")
cat("R validation passed:", nrow(carbonate), "carbonate vertices;", nrow(sites), "verified sites\n")
