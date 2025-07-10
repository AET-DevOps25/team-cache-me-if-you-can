#terraform {
  #required_providers {
    #kubernetes = {
    #  source  = "hashicorp/kubernetes"
   #   version = "~> 2.13"
  #  }
 # }
#}

provider "kubernetes" {
  config_path    = pathexpand("~/.kube/config")
  config_context = "student"
}
