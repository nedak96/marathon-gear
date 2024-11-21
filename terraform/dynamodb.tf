resource "aws_dynamodb_table" "marathon_gear_store_info" {
  name           = "marathon_gear_store_info"
  hash_key       = "store"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1

  attribute {
    name = "store"
    type = "S"
  }
}
