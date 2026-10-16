# use the first two availability zones of the region
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# VPC with two public subnets
# no NAT gateway because it costs money every hour, so the nodes are in public subnets
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.21"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"
  azs  = local.azs

  public_subnets          = ["10.0.1.0/24", "10.0.2.0/24"]
  map_public_ip_on_launch = true
  enable_nat_gateway      = false
  enable_dns_hostnames    = true

  # tag needed so load balancers can use these subnets
  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }
}

# EKS cluster with one managed node group
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.31"

  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version

  # the API is public but only my IP can reach it
  cluster_endpoint_public_access       = true
  cluster_endpoint_public_access_cidrs = var.api_access_cidrs

  # gives my IAM user admin access to the cluster
  enable_cluster_creator_admin_permissions = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets

  cluster_addons = {
    coredns    = {}
    kube-proxy = {}
    vpc-cni    = {}
  }

  eks_managed_node_groups = {
    default = {
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = [var.node_instance_type]
      min_size       = 1
      max_size       = 2
      desired_size   = 2
    }
  }
}
