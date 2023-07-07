from constructs import Construct
from aws_cdk import Stack, Environment


class Demo(Stack):
    def __init__(
        self,
        scope: "Construct",
        construct_id: "str",
        env: "Environment",
    ):
        super().__init__(scope, construct_id, env=env)
