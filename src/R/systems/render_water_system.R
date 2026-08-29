args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) > 0) args[[1]] else "."
lines_path <- file.path(root, "outputs", "tables", "water_map_render_data.csv")
points_path <- file.path(root, "outputs", "tables", "water_facilities_render_data.csv")
out_path <- file.path(root, "outputs", "figures", "water_system_R_validation.png")

stopifnot(file.exists(lines_path), file.exists(points_path))
ln <- read.csv(lines_path, stringsAsFactors = FALSE)
pt <- read.csv(points_path, stringsAsFactors = FALSE)
stopifnot(nrow(ln) > 0, nrow(pt) >= 2)

png(out_path, width = 1800, height = 1100, res = 160, bg = "#f7f5ef")
par(mar = c(4, 4, 6, 2), fg = "#18333f", col.axis = "#18333f", col.lab = "#18333f")
plot(range(ln$longitude), range(ln$latitude), type = "n", asp = 1,
     xlab = "Longitude", ylab = "Latitude",
     main = "Independent R render - Maumee Water System v0.1",
     sub = "Solid: USGS NHDPlus Lower Maumee; dashed: inferred WBD HUC-12 routing")
for (id in unique(ln$line_id)) {
  z <- ln[ln$line_id == id, ]
  z <- z[order(z$seq), ]
  inferred <- z$render_class[[1]] == "inferred_huc_route"
  lines(z$longitude, z$latitude, col = if (inferred) "#78aabd" else "#2d7ea7",
        lwd = if (inferred) 0.6 else 0.9, lty = if (inferred) 2 else 1)
}
points(pt$longitude, pt$latitude, pch = 21, bg = c("#c85f46", "#18333f"), col = "white", cex = 1.5)
short_labels <- c("Toledo intake (GLOS)", "Collins Park WTP")
text(pt$longitude, pt$latitude, labels = short_labels, pos = 4, cex = 0.65)
legend("bottomleft", legend = c("NHDPlus physical flowline", "WBD topology connector"),
       col = c("#2d7ea7", "#78aabd"), lty = c(1, 2), lwd = c(1, 1), cex = 0.7, bty = "n")
mtext("QA render only - Python outputs remain the publication maps", side = 3, line = 0.5, cex = 0.65)
dev.off()
cat(out_path, "\n")
