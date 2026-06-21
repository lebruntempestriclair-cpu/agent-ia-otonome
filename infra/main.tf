# Infrastructure as Code - Déploiement Cloud (Terraform)

provider "aws" {
  region = var.aws_region
}

# 1. Bucket S3 pour les médias
resource "aws_s3_bucket" "dubbing_media" {
  bucket = "dubbing-platform-media-${var.environment}"
}

resource "aws_s3_bucket_public_access_block" "block" {
  bucket = aws_s3_bucket.dubbing_media.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 2. Redis pour la file d'attente
resource "aws_elasticache_cluster" "task_queue" {
  cluster_id           = "dubbing-queue-${var.environment}"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}

# 3. Cluster EKS pour les microservices
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "dubbing-cluster-${var.environment}"
  cluster_version = "1.27"

  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnets

  eks_managed_node_groups = {
    cpu_nodes = {
      min_size     = 1
      max_size     = 10
      desired_size = 2
      instance_types = ["t3.medium"]
    }
    gpu_nodes = {
      min_size     = 0
      max_size     = 5
      desired_size = 1
      instance_types = ["g4dn.xlarge"] # Pour Wav2Lip/Whisper
    }
  }
}

# Variables
variable "aws_region" { default = "eu-west-3" }
variable "environment" { default = "staging" }
variable "vpc_id" { type = string }
variable "private_subnets" { type = list(string) }
