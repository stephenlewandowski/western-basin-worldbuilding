args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) > 0) args[[1]] else "."
poly_path <- file.path(root, "outputs", "tables", "materials_carbonate_render_data.csv")
site_path <- file.path(root, "outputs", "tables", "materials_sites_render_data.csv")
out_path <- file.path(root, "outputs", "figures", "materials_system_R_validation.png")

carbonate <- read.csv(poly_path, stringsAsFactors = FALSE)
sites <- read.csv(site_path, stringsAsFactors = FALSE)
stopifnot(nrow(carbonate) > 100, nrow(sites) == 5)

png(out_path, width = 1800, height = 1100, res = 160, bg = "#f3efe5")
par(mar = c(4, 4, 6, 2), fg = "#18333f", col.axis = "#18333f", col.lab = "#18333f")
plot(range(carbonate$longitude), range(carbonate$latitude), type = "n", asp = 1,
     xlab = "Longitude", ylab = "Latitude",
     main = "Independent R render - Geology + Strategic Materials 2026",
     sub = "Layer-derived render tables; publication artifact is Map 06")
groups <- unique(paste(carbonate$feature_id, carbonate$part, sep = ":"))
for (id in groups) {
  z <- carbonate[paste(carbonate$feature_id, carbonate$part, sep = ":") == id, ]
  z <- z[order(z$seq), ]
  polygon(z$longitude, z$latitude, col = adjustcolor("#d4bc69", alpha.f = 0.22),
          border = "#9c854c", lwd = 0.35)
}
site_colors <- c(extraction = "#c18d22", primary_processing = "#c18d22",
                 advanced_processing = "#8f4f77", legacy_cleanup = "#b95142")
site_pch <- c(extraction = 22, primary_processing = 22, advanced_processing = 24, legacy_cleanup = 23)
points(sites$longitude, sites$latitude, pch = site_pch[sites$supply_chain_role],
       bg = site_colors[sites$supply_chain_role], col = "white", cex = 1.5)
text(sites$longitude, sites$latitude, labels = sites$feature_name, pos = 4, cex = 0.56)
legend("bottomleft", legend = c("Local carbonate extraction/processing", "External-feed advanced processing", "Legacy cleanup"),
       pch = c(22, 24, 23), pt.bg = c("#c18d22", "#8f4f77", "#b95142"), col = "white", cex = 0.7, bty = "n")
mtext("No production quantities, groundwater-flow arrows, speculative corridor, or future scenario", side = 3, line = 0.4, cex = 0.66)
dev.off()
cat(out_path, "\n")
