locals {
  python_dependencies_path = "${path.module}/files/python-dependencies-layer"
  chromium_dependencies_path = "${path.module}/files/chromium-dependencies-layer"
}

resource "terraform_data" "install_python_dependencies" {
  provisioner "local-exec" {
    command = "bash ${path.module}/../scripts/create_dependency_zip.sh"
    environment = {
      PATH_MODULE       = path.module
      PYTHON_DEPENDENCIES_PATH = "${local.python_dependencies_path}/python"
      CHROMIUM_DEPENDENCIES_PATH = local.chromium_dependencies_path
    }
  }
  triggers_replace = {
    requirements = [
      filebase64sha256("${path.module}/../requirements.txt"),
      filebase64sha256("${path.module}/../scripts/create_dependency_zip.sh"),
    ]
  }
}

data "archive_file" "python_dependencies_zip" {
  type        = "zip"
  output_path = "${path.module}/files/python-dependencies-layer.zip"
  source_dir  = local.python_dependencies_path
  depends_on  = [terraform_data.install_python_dependencies]
}

data "archive_file" "chromium_dependencies_zip" {
  type        = "zip"
  output_path = "${path.module}/files/chromium-dependencies-layer.zip"
  source_dir  = local.chromium_dependencies_path
  depends_on  = [terraform_data.install_python_dependencies]
}

resource "aws_lambda_layer_version" "python_dependencies_lambda_layer" {
  filename            = data.archive_file.python_dependencies_zip.output_path
  layer_name          = "python-dependencies-layer"
  compatible_runtimes = [local.runtime]
  source_code_hash    = data.archive_file.python_dependencies_zip.output_base64sha256
}

resource "aws_lambda_layer_version" "chromium_dependencies_lambda_layer" {
  filename            = data.archive_file.chromium_dependencies_zip.output_path
  layer_name          = "chromium-dependencies-layer"
  compatible_runtimes = [local.runtime]
  source_code_hash    = data.archive_file.chromium_dependencies_zip.output_base64sha256
}
