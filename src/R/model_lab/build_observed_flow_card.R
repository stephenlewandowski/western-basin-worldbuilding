# Presentation of an existing observed record; independent of the routing engine.
# From repository root, first run the Python record builder, then this script.
rows <- read.csv("outputs/model_lab/observations/waterville_daily_flow_2025.csv",
                 stringsAsFactors = FALSE)
days <- as.Date(rows$date)
flow <- rows$daily_mean_discharge_ft3_s
stopifnot(nrow(rows) == 365L, !anyDuplicated(days), all(is.finite(flow)), all(flow >= 0))
draw <- function() {
  par(mar = c(3.5, 5, 1, 1), mgp = c(3, 0.6, 0), las = 1,
      col.axis = "#42595d", col.lab = "#254b53", fg = "#8a9b96", cex.axis = 0.9)
  plot(days, flow, type = "n", ylim = c(0, 72000), xlab = "", ylab = "Daily mean (ft³/s)",
       axes = FALSE, yaxs = "i", xaxs = "i")
  abline(h = c(0, 20000, 40000, 60000), col = "#d7dcd3", lwd = 0.8)
  axis(2, at = c(0, 20000, 40000, 60000), labels = c("0", "20,000", "40,000", "60,000"), tick = FALSE)
  ticks <- as.Date(paste0("2025-", sprintf("%02d", seq(1, 11, 2)), "-01"))
  axis(1, at = ticks, labels = c("Jan", "Mar", "May", "Jul", "Sep", "Nov"), tick = FALSE)
  lines(days, flow, col = "#254b53", lwd = 1.3)
  provisional <- rows$approval_in_snapshot == "provisional"
  points(days[provisional], flow[provisional], pch = 1, cex = 0.65, col = "#ad603f", lwd = 1.3)
  estimated <- tolower(as.character(rows$estimated)) == "true"
  points(days[estimated], flow[estimated], pch = 17, cex = 0.65, col = "#254b53")
  box(bty = "l")
}
svg("outputs/model_lab/observations/waterville_daily_flow_2025.svg",
    width = 10, height = 4.2, pointsize = 12, bg = "#f4f1e9")
draw()
invisible(dev.off())
cat("Built the observed-flow card; no routing/model calculation.\n")
