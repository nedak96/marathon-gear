data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "marathon_gear_role" {
  name               = "marathon-gear-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

data "aws_iam_policy_document" "marathon_gear_policy_doc" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem"
    ]
    resources = [aws_dynamodb_table.marathon_gear_store_info.arn]
  }
}

resource "aws_iam_policy" "marathon_gear_policy" {
  name        = "marathon-gear-policy"
  description = "Policy for the marathon gear function"
  policy      = data.aws_iam_policy_document.marathon_gear_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "marathon_gear" {
  role       = aws_iam_role.marathon_gear_role.name
  policy_arn = aws_iam_policy.marathon_gear_policy.arn
}
