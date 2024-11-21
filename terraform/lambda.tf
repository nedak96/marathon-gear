locals {
  path_source_code = "${path.module}/.."
  function_name    = "marathon-gear"
  runtime          = "python3.11"
}

data "archive_file" "source_code_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/files/marathon-gear.zip"
}

resource "aws_lambda_function" "marathon_gear" {
  filename         = data.archive_file.source_code_zip.output_path
  function_name    = local.function_name
  role             = aws_iam_role.marathon_gear_role.arn
  handler          = "marathon_gear.handler"
  runtime          = local.runtime
  timeout          = 60
  source_code_hash = data.archive_file.source_code_zip.output_base64sha256
  layers           = [
    aws_lambda_layer_version.python_dependencies_lambda_layer.arn,
    aws_lambda_layer_version.chromium_dependencies_lambda_layer.arn,
  ]
  environment {
    variables = {
      STORE_INFO_TABLE = aws_dynamodb_table.marathon_gear_store_info.name
      GMAIL_ADDRESS         = var.gmail_address
      GMAIL_PASSWORD          = var.gmail_password
      RECIPIENTS          = join(",", var.recipients)
      SE_AVOID_STATS     = "true"
    }
  }
}

resource "aws_cloudwatch_log_group" "marathon_gear_lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.marathon_gear.function_name}"
  retention_in_days = 3
}

resource "aws_cloudwatch_event_rule" "marathon_gear_rule" {
  name                = "marathon-gear-rule"
  description         = "Fires every minute"
  schedule_expression = "rate(1 minute)"
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
