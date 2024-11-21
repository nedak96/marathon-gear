
variable "gmail_address" {
  description = "Service Gmail Address"
  type        = string
}

variable "gmail_password" {
  description = "Service Gmail Password"
  type        = string
  # Uncomment to remove from AWS console
  # sensitive   = true
}

variable "recipients" {
  description = "Recipients"
  type        = list(string)
}
