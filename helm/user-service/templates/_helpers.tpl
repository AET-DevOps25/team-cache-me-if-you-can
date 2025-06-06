{{/*
Expand the name of the chart.
*/}}
{{- define "user-service.name" -}}
{{ .Chart.Name }}
{{- end }}

{{/*
Create a fullname by combining release name and chart name.
*/}}
{{- define "user-service.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}

{{/*
Helper for chart label.
*/}}
{{- define "user-service.chart" -}}
{{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}
