resource "aws_ecr_repository" "marathon_gear_repo" {
  name = "marathon-gear-repo"
}

data "aws_ecr_authorization_token" "token" {}

provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.token.proxy_endpoint
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

resource "docker_image" "marathon_gear_image" {
  name = "${aws_ecr_repository.marathon_gear_repo.repository_url}:latest"
  build {
    context = "${path.module}/.."
  }
  force_remove = true
  platform     = "linux/amd64"
  triggers = {
    "src_sha"          = sha1(join("", [for f in fileset(path.module, "../src/**/*") : filesha1(f)]))
    "requirements_sha" = filesha1("${path.module}/../requirements.txt"),
    "dockerfile_sha"   = filesha1("${path.module}/../Dockerfile"),
  }
}

resource "docker_registry_image" "marathon_gear_image" {
  name = docker_image.marathon_gear_image.name

  triggers = {
    "image_id" : docker_image.marathon_gear_image.image_id,
  }
}
