resource "aws_instance" "web" {
  ami           = "test"
  instance_type = "t3.small"
}

output "instance_detail" {
  value = aws_instance.web.id
}
