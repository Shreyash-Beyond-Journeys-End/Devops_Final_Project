# Terraform (AWS VPC + EKS)

Makes a VPC with 2 public subnets and an EKS cluster with 2 `t3.small` nodes in ap-south-1.

AWS credentials come from `aws configure`, they are not in these files.

Steps:

```bash
cp terraform.tfvars.example terraform.tfvars   # then put your own ip in it
terraform init
terraform plan -out=tfplan
terraform apply tfplan     # takes around 15 min
aws eks update-kubeconfig --region ap-south-1 --name placetrack
kubectl get nodes
terraform destroy          # delete everything after, EKS costs money per hour
```
