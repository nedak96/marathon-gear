locals {
  path_source_code = "${path.module}/.."
  function_name    = "marathon-gear"
  runtime          = "python3.11"
}

resource "aws_lambda_function" "marathon_gear" {
  depends_on = [
    docker_registry_image.marathon_gear_image,
    aws_cloudwatch_log_group.marathon_gear_lambda_logs,
  ]
  function_name    = local.function_name
  role             = aws_iam_role.marathon_gear_role.arn
  image_uri        = docker_registry_image.marathon_gear_image.name
  source_code_hash = docker_registry_image.marathon_gear_image.sha256_digest
  memory_size      = 1024
  package_type     = "Image"
  timeout          = 300
  environment {
    variables = {
      STORE_INFO_TABLE = aws_dynamodb_table.marathon_gear_store_info.name
      GMAIL_ADDRESS    = var.gmail_address
      GMAIL_PASSWORD   = var.gmail_password
      RECIPIENTS       = join(",", var.recipients)
    }
  }
}

resource "aws_cloudwatch_log_group" "marathon_gear_lambda_logs" {
  name              = "/aws/lambda/${local.function_name}"
  retention_in_days = 3
}

resource "aws_cloudwatch_event_rule" "marathon_gear_rule" {
  name                = "marathon-gear-rule"
  description         = "Fires every minute"
  schedule_expression = "rate(30 minutes)"
}

resource "aws_cloudwatch_event_target" "marathon_gear_every_minute" {
  rule      = aws_cloudwatch_event_rule.marathon_gear_rule.name
  target_id = "marathon-gear-every-minute"
  arn       = aws_lambda_function.marathon_gear.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_lambda_trigger" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.marathon_gear.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.marathon_gear_rule.arn
}
