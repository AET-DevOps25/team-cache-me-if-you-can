{{/*
Expand the name of the chart.
*/}}
{{- define "group-service.name" -}}
{{ .Chart.Name }}
{{- end }}

{{/*
Create a fullname by combining release name and chart name.
*/}}
{{- define "group-service.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}

{{/*
Helper for chart label.
*/}}
{{- define "group-service.chart" -}}
{{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}
