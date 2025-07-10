
output "user_service_name" {
  value = kubernetes_service.user.metadata[0].name
}
output "group_service_name" {
  value = kubernetes_service.group.metadata[0].name
}
output "gateway_service_name" {
  value = kubernetes_service.gateway.metadata[0].name
}
