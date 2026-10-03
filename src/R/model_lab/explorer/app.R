# Read-only viewer for the committed Model Lab v0.1B synthetic diagnostics.
# Launch from the repository root with shiny::runApp("src/R/model_lab/explorer").

if (!requireNamespace("shiny", quietly = TRUE)) {
  stop("The Model Lab explorer requires the R package 'shiny'.", call. = FALSE)
}

library(shiny)

find_repo_root <- function(start = getwd()) {
  candidate <- normalizePath(start, winslash = "/", mustWork = TRUE)
  repeat {
    if (file.exists(file.path(candidate, "data", "model_lab", "v01b_sensitivity.json"))) {
      return(candidate)
    }
    parent <- dirname(candidate)
    if (identical(parent, candidate)) {
      stop("Run the explorer from its repository checkout.", call. = FALSE)
    }
    candidate <- parent
  }
}

repo_root <- find_repo_root()
source(file.path(repo_root, "src", "R", "model_lab", "explorer", "data.R"), local = TRUE)
lab <- load_model_lab(repo_root)

# GeoJSON is used only as HUC polygon context. No line is drawn between HUCs:
# the routing ledger's accounting links are not mapped stream channels.
ring_xy <- function(ring) {
  if (is.matrix(ring)) return(ring[, 1:2, drop = FALSE])
  rows <- lapply(ring, function(point) as.numeric(unlist(point, use.names = FALSE)[1:2]))
  do.call(rbind, rows)
}

geometry_paths <- function(geometry) {
  polygons <- switch(
    geometry$type,
    Polygon = list(geometry$coordinates),
    MultiPolygon = geometry$coordinates,
    stop("Unsupported WBD geometry type: ", geometry$type, call. = FALSE)
  )
  lapply(polygons, function(polygon) {
    rings <- lapply(polygon, ring_xy)
    xs <- unlist(lapply(rings, function(ring) c(ring[, 1], NA_real_)), use.names = FALSE)
    ys <- unlist(lapply(rings, function(ring) c(ring[, 2], NA_real_)), use.names = FALSE)
    data.frame(
      x = xs[-length(xs)],
      y = ys[-length(ys)]
    )
  })
}

map_paths <- lapply(lab$geography$geometry, geometry_paths)
map_xy <- do.call(rbind, unlist(map_paths, recursive = FALSE))
map_xrange <- range(map_xy$x, na.rm = TRUE)
map_yrange <- range(map_xy$y, na.rm = TRUE)
map_xrange <- map_xrange + c(-1, 1) * diff(map_xrange) * 0.035
map_yrange <- map_yrange + c(-1, 1) * diff(map_yrange) * 0.035

case_choices <- setNames(names(lab$runs), vapply(lab$runs, function(run) run$label, character(1)))
huc_labels <- ifelse(
  is.na(lab$geography$name) | !nzchar(lab$geography$name),
  lab$geography$huc12,
  paste0(lab$geography$huc12, " | ", lab$geography$name)
)
huc_choices <- setNames(lab$geography$huc12, huc_labels)

metric_number <- function(value) format(as.numeric(value), trim = TRUE, scientific = FALSE, digits = 7)
blank_none <- function(value) {
  value <- as.character(value)
  value[is.na(value) | !nzchar(value)] <- "(none)"
  value
}

ui <- fluidPage(
  title = "Model Lab Explorer | Western Basin Atlas",
  tags$head(tags$style(HTML("\n    body { background: #f3f6f5; color: #18323b; font-family: system-ui, sans-serif; }\n    .container-fluid { max-width: 1480px; margin: auto; padding: 18px 25px 42px; }\n    h1 { font-size: 2.2rem; font-weight: 680; margin-bottom: 8px; }\n    h2 { font-size: 1.42rem; font-weight: 650; margin-top: 0; }\n    h3 { font-size: 1.12rem; font-weight: 650; margin-top: 0; }\n    .intro { max-width: 950px; line-height: 1.5; margin-bottom: 20px; }\n    .notice { border-left: 4px solid #b35b30; background: #fff6ed; padding: 11px 14px; }\n    .panel-card { background: white; border: 1px solid #d8e0df; border-radius: 8px;\n                  padding: 18px; margin-bottom: 20px; box-shadow: 0 1px 3px #263b3b10; }\n    .panel-card p { line-height: 1.45; }\n    .control-card label { font-weight: 600; }\n    .control-card .form-group { margin-bottom: 18px; }\n    .legend { display: flex; flex-wrap: wrap; gap: 7px 18px; margin: 8px 0 0; font-size: 0.94em; }\n    .legend-item { display: inline-flex; align-items: center; gap: 6px; }\n    .swatch { display: inline-block; width: 15px; height: 15px; border: 1px solid #688087; }\n    .table-scroll { overflow-x: auto; overflow-y: auto; max-height: 450px; }\n    .table-scroll table { margin-bottom: 0; }\n    .table-scroll th { position: sticky; top: 0; z-index: 1; background: #f2f6f5; }\n    .table-scroll td, .table-scroll th { white-space: nowrap; }\n    .provenance-table td { white-space: normal; overflow-wrap: anywhere; }\n    .minor { font-size: 0.91em; color: #405760; }\n    .run-facts dt { float: left; clear: left; min-width: 145px; font-weight: 650; }\n    .run-facts dd { margin-left: 150px; overflow-wrap: anywhere; }\n    @media (max-width: 767px) {\n      .container-fluid { padding: 12px 12px 30px; }\n      h1 { font-size: 1.75rem; }\n      .panel-card { padding: 13px; margin-bottom: 13px; }\n      #huc_map { height: 320px !important; }\n      #mass_chart { height: 270px !important; }\n      .run-facts dt { float: none; }\n      .run-facts dd { margin-left: 0; margin-bottom: 8px; }\n    }\n  "))),
  h1("Western Basin Model Lab - Explorer"),
  p(class = "minor", "Explorer v0.2A | Saved Model Lab v0.1B diagnostics"),
  p(class = "intro notice",
    strong("Synthetic accounting diagnostics only. "),
    "Values are unit pulses, not measured water or nutrient loads. HUC polygons locate accounting units; the display does not map stream channels, travel time, or source-attributed delivery."
  ),
  fluidRow(
    column(3, div(class = "panel-card control-card",
      h2("Explore a run"),
      selectInput("case", "Synthetic case", choices = case_choices, selected = "strict"),
      selectInput("constituent", "Constituent", choices = c("Water" = "water", "Total nitrogen" = "TN", "Total phosphorus" = "TP")),
      selectInput("huc", "Focus HUC-12", choices = huc_choices, selected = lab$default_huc),
      radioButtons("direction", "Trace direction", choices = c("Downstream" = "downstream", "Upstream" = "upstream"), selected = "downstream"),
      p(class = "minor", "Switching cases changes only the displayed saved run. The explorer never executes or modifies the model.")
    )),
    column(9, div(class = "panel-card",
      h2("HUC accounting map"),
      tags$span(class = "sr-only", "HUC-12 polygons colored by selected trace reachability and focus."),
      plotOutput("huc_map", height = "460px"),
      div(class = "legend",
        span(class = "legend-item", span(class = "swatch", style = "background:#194d63;"), "Selected HUC"),
        span(class = "legend-item", span(class = "swatch", style = "background:#83b8bd;"), "Policy reachable"),
        span(class = "legend-item", span(class = "swatch", style = "background:#e8ad72;"), "Structural path, not policy reachable"),
        span(class = "legend-item", span(class = "swatch", style = "background:transparent;border:2px dashed #9b4d1b;"), "Unresolved link source"),
        span(class = "legend-item", span(class = "swatch", style = "background:#e6eceb;"), "Other HUCs")
      ),
      p(class = "minor", "Colors represent topology and the selected routing policy. They do not encode water or nutrient quantity.")
    ))
  ),
  fluidRow(
    column(7, div(class = "panel-card",
      h2("Trace records"),
      textOutput("trace_caption"),
      div(class = "table-scroll", tableOutput("trace_table")),
      p(class = "minor", "The first unresolved link is recorded along the route from the traced HUC toward the focus for upstream traces, and from the focus toward the traced HUC for downstream traces. Reachability is a routing-policy condition, not a measured contribution.")
    )),
    column(5, div(class = "panel-card",
      h2("Selected HUC ledger"),
      textOutput("ledger_caption"),
      div(class = "table-scroll", tableOutput("ledger_table")),
      p(class = "minor", "Not forwarded and unrouted are accounting dispositions; neither is measured storage, treatment, or nutrient removal.")
    ))
  ),
  fluidRow(
    column(7, div(class = "panel-card",
      h2("Three-case mass disposition"),
      p(class = "minor", "Same synthetic input and selected constituent in each saved case; bars sum to supplied units."),
      tags$span(class = "sr-only", "Stacked bars comparing boundary export, unresolved unrouted amount, and assumption-based not-forwarded amount."),
      plotOutput("mass_chart", height = "310px"),
      div(class = "legend",
        span(class = "legend-item", span(class = "swatch", style = "background:#327a8b;"), "Boundary export"),
        span(class = "legend-item", span(class = "swatch", style = "background:#e8ad72;"), "Unrouted at unresolved link"),
        span(class = "legend-item", span(class = "swatch", style = "background:#9e8bb7;"), "Not forwarded (assumed)")
      ),
      div(class = "table-scroll", tableOutput("mass_table"))
    )),
    column(5, div(class = "panel-card",
      h2("Run and scientific boundaries"),
      uiOutput("run_facts"),
      h3("Interpretation limits"),
      uiOutput("limitations")
    ))
  ),
  div(class = "panel-card provenance-table",
    h2("Input and code provenance"),
    p(class = "minor", "Paths and SHA-256 values come from the saved run manifest. Source and code hashes are checked at startup, allowing Git's LF/CRLF line-ending conversion."),
    div(class = "table-scroll", tableOutput("source_table"))
  )
)

server <- function(input, output, session) {
  active_run <- reactive(lab$runs[[req(input$case)]])
  active_trace <- reactive(trace_for(active_run(), req(input$direction), req(input$huc)))
  active_balance <- reactive({
    rows <- balance_for(active_run(), req(input$constituent))
    rows[rows$huc12 == req(input$huc), , drop = FALSE]
  })
  case_summaries <- reactive({
    do.call(rbind, lapply(names(lab$runs), function(case_key) {
      row <- summary_for(lab$runs[[case_key]], req(input$constituent))
      data.frame(
        case = lab$runs[[case_key]]$label,
        unit = row$unit,
        supplied = row$total_local_input,
        boundary_export = row$boundary_export,
        unrouted = row$total_unrouted_at_unresolved,
        not_forwarded = row$total_not_forwarded_assumed,
        residual = row$residual,
        stringsAsFactors = FALSE
      )
    }))
  })

  output$huc_map <- renderPlot({
    trace <- active_trace()
    reachable <- trace$traced_huc12[trace$policy_reachable]
    blocked <- trace$traced_huc12[!trace$policy_reachable]
    focus <- req(input$huc)
    fills <- rep("#e6eceb", length(map_paths))
    fills[lab$geography$huc12 %in% reachable] <- "#83b8bd"
    fills[lab$geography$huc12 %in% blocked] <- "#e8ad72"
    fills[lab$geography$huc12 == focus] <- "#194d63"
    par(mar = c(2.0, 2.0, 0.5, 0.5), bg = "white")
    plot.new()
    plot.window(xlim = map_xrange, ylim = map_yrange,
                asp = 1 / cos(mean(map_yrange) * pi / 180))
    for (i in seq_along(map_paths)) {
      for (part in map_paths[[i]]) {
        graphics::polypath(part$x, part$y, col = fills[i], border = "#91a19f", lwd = 0.25, rule = "evenodd")
      }
    }
    focus_index <- match(focus, lab$geography$huc12)
    if (!is.na(focus_index)) {
      for (part in map_paths[[focus_index]]) {
        graphics::polypath(part$x, part$y, col = NA, border = "#123b51", lwd = 1.4, rule = "evenodd")
      }
    }
    unresolved_sources <- unique(trace$first_unresolved_link_from_huc12)
    unresolved_sources <- unresolved_sources[!is.na(unresolved_sources) & nzchar(unresolved_sources)]
    for (source_huc in unresolved_sources) {
      source_index <- match(source_huc, lab$geography$huc12)
      if (!is.na(source_index)) {
        for (part in map_paths[[source_index]]) {
          graphics::polypath(part$x, part$y, col = NA, border = "#9b4d1b", lwd = 1.5, lty = 2, rule = "evenodd")
        }
      }
    }
    box(col = "#d8e0df")
  }, res = 100)

  output$trace_caption <- renderText({
    count <- nrow(active_trace())
    paste0(count, if (count == 1L) " HUC record" else " HUC records", " on the ", input$direction,
           " structural trace from ", input$huc, ".")
  })
  output$trace_table <- renderTable({
    rows <- active_trace()[order(active_trace()$hops, active_trace()$traced_huc12), , drop = FALSE]
    data.frame(
      `Traced HUC-12` = rows$traced_huc12,
      Hops = rows$hops,
      `Policy reachable` = ifelse(rows$policy_reachable, "Yes", "No"),
      `First unresolved link from HUC-12` = blank_none(rows$first_unresolved_link_from_huc12),
      check.names = FALSE
    )
  }, striped = TRUE, spacing = "xs", rownames = FALSE)

  output$ledger_caption <- renderText({
    rows <- active_balance()
    if (nrow(rows) != 1L) return("No ledger row found for this selection.")
    paste(input$huc, input$constituent, rows$unit, sep = " | ")
  })
  output$ledger_table <- renderTable({
    rows <- active_balance()
    validate(need(nrow(rows) == 1L, "No ledger row found for this selection."))
    fields <- c(
      "Local input" = "local_input", "Upstream in" = "upstream_in",
      "Available" = "available", "Pass-through assumption" = "pass_through",
      "Not forwarded (assumed)" = "not_forwarded_assumed",
      "Unrouted at unresolved link" = "unrouted_at_unresolved",
      "Downstream out" = "downstream_out", "Boundary export" = "boundary_export",
      "Balance residual" = "residual"
    )
    data.frame(
      Field = c(names(fields), "Next HUC", "Routing basis", "Routing QA", "Input status"),
      Value = c(vapply(fields, function(field) metric_number(rows[[field]]), character(1)),
                blank_none(rows$route_to_huc12), rows$routing_basis,
                rows$qa_status, rows$input_status),
      check.names = FALSE
    )
  }, striped = TRUE, spacing = "xs", rownames = FALSE)

  output$mass_chart <- renderPlot({
    rows <- case_summaries()
    values <- rbind(
      "Boundary export" = rows$boundary_export,
      "Unrouted" = rows$unrouted,
      "Not forwarded (assumed)" = rows$not_forwarded
    )
    short_case_names <- c(strict = "Strict", assume_wbd = "WBD successor", tn_half_pass = "TN half-pass")
    par(mar = c(3.8, 9.5, 0.8, 1), bg = "white")
    barplot(values, horiz = TRUE, names.arg = unname(short_case_names[names(lab$runs)]), las = 1,
            col = c("#327a8b", "#e8ad72", "#9e8bb7"),
            border = NA, xlim = c(0, max(rows$supplied) * 1.08),
            xlab = paste("Synthetic", rows$unit[1]), cex.names = 0.8)
  }, res = 100)
  output$mass_table <- renderTable({
    rows <- case_summaries()
    data.frame(
      Case = rows$case,
      Supplied = vapply(rows$supplied, metric_number, character(1)),
      `Boundary export` = vapply(rows$boundary_export, metric_number, character(1)),
      Unrouted = vapply(rows$unrouted, metric_number, character(1)),
      `Not forwarded (assumed)` = vapply(rows$not_forwarded, metric_number, character(1)),
      Residual = vapply(rows$residual, metric_number, character(1)),
      check.names = FALSE
    )
  }, striped = TRUE, spacing = "xs", rownames = FALSE)

  output$run_facts <- renderUI({
    run <- active_run()
    manifest <- run$manifest
    tags$div(
      tags$p(strong(run$label), ": ", run$description),
      tags$dl(class = "run-facts",
        tags$dt("Run ID"), tags$dd(manifest$run_id),
        tags$dt("Schema"), tags$dd(manifest$schema_version),
        tags$dt("Period"), tags$dd(manifest$period),
        tags$dt("Unresolved links"), tags$dd(manifest$unresolved_policy),
        tags$dt("Input status"), tags$dd(manifest$input_status),
        tags$dt("Topology"), tags$dd(paste(manifest$topology$huc_count, "HUC-12 units;",
                                             manifest$topology$unresolved_link_count, "unresolved links"))
      )
    )
  })
  output$limitations <- renderUI({
    limits <- active_run()$manifest$interpretation
    tags$ul(lapply(limits, tags$li))
  })
  output$source_table <- renderTable({
    files <- active_run()$manifest$source_files
    rows <- lapply(names(files), function(item) {
      value <- files[[item]]
      if (is.null(value)) {
        return(data.frame(Source = item, Path = "Not used", SHA256 = "(none)"))
      }
      if (is.list(value)) {
        return(data.frame(Source = item, Path = blank_none(value$path), SHA256 = blank_none(value$sha256)))
      }
      data.frame(Source = item, Path = "Code hash", SHA256 = as.character(value))
    })
    do.call(rbind, rows)
  }, striped = TRUE, spacing = "xs", rownames = FALSE)
}

shinyApp(ui, server)
