root <- if(length(commandArgs(trailingOnly=TRUE))) commandArgs(trailingOnly=TRUE)[1] else '.'
r <- function(p) read.csv(file.path(root,p),stringsAsFactors=FALSE,check.names=FALSE)
a<-r('data/processed/scenarios/environmental_health_scenario_assumptions.csv');n<-r('data/processed/scenarios/exposure_nodes_scenario.csv');e<-r('data/processed/scenarios/exposure_edges_scenario.csv');c<-r('data/processed/scenarios/exposure_controls_scenario.csv');u<-r('data/processed/scenarios/exposure_uncertainty_scenario.csv');x<-r('outputs/figures/environmental_health_scenarios_comparison.csv')
stopifnot(nrow(a)==36,nrow(n)==30,nrow(e)==30,nrow(c)==30,nrow(u)==30,nrow(x)==6)
stopifnot(all(nzchar(a$scenario_id)),all(nzchar(n$scenario_year)),all(n$reality_status=='fictional'))
stopifnot(setequal(unique(a$scenario_id),c('A','B','C')),setequal(unique(a$scenario_year),c(2050,2075)))
text<-tolower(paste(capture.output(write.csv(a,'')),collapse=' '));stopifnot(!grepl('dose score|exposure score|mortality|epidemiology|mosquito',text))
cat('status=passed\nphase=7C\nassumptions=36\nscenario_nodes=30\nscenario_edges=30\ncontrol_states=30\nuncertainty_states=30\ncomparison_rows=6\nqualitative_only=TRUE\n')
