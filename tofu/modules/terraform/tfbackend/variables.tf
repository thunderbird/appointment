variable "bucket_name" {
  description = "TF state S3 bucket name"
  type        = string
}

variable "table_name" {
  description = "TF locks Dynamodb table name"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
}

