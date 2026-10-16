variable "region" {
  type    = string
  default = "ap-south-1" # mumbai
}

variable "cluster_name" {
  type    = string
  default = "placetrack"
}

variable "kubernetes_version" {
  type    = string
  default = "1.35"
}

# t3.small because t3.medium is not allowed on my aws plan
variable "node_instance_type" {
  type    = string
  default = "t3.small"
}

# put your own public ip here in terraform.tfvars, like ["1.2.3.4/32"]
variable "api_access_cidrs" {
  type        = list(string)
  description = "IPs that are allowed to reach the EKS API"
}
