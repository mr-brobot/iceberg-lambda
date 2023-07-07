from constructs import Construct
from aws_cdk import Stack, Environment, Duration
from aws_cdk.aws_iam import PolicyStatement, Effect
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_lambda import (
    DockerImageFunction,
    DockerImageCode,
    Tracing,
    Architecture,
)
from aws_cdk.aws_ecr_assets import Platform
from aws_cdk.aws_glue_alpha import Database, Table


class PyIcebergFunction(DockerImageFunction):
    def __init__(
        self,
        scope: "Construct",
        construct_id: "str",
        database: "Database",
        table: "Table",
        bucket: "Bucket",
    ):
        image_code = DockerImageCode.from_image_asset(
            "demo/function", platform=Platform.LINUX_ARM64, cmd=["app.handler"]
        )

        super().__init__(
            scope,
            construct_id,
            code=image_code,
            architecture=Architecture.ARM_64,
            memory_size=1024,
            timeout=Duration.seconds(30),
            tracing=Tracing.ACTIVE,
            environment={
                "ICEBERG_DATABASE_NAME": database.database_name,
                "ICEBERG_TABLE_NAME": table.table_name,
                "PYICEBERG_CATALOG__GLUE__TYPE": "glue",
            },
        )

        bucket.grant_read(self)

        account_id = Stack.of(self).account
        region = Stack.of(self).region
        self.add_to_role_policy(
            PolicyStatement(
                effect=Effect.ALLOW,
                actions=["glue:GetTable"],
                resources=[
                    f"arn:aws:glue:{region}:{account_id}:catalog",
                    database.database_arn,
                    table.table_arn,
                ],
            )
        )


class Demo(Stack):
    def __init__(
        self,
        scope: "Construct",
        construct_id: "str",
        env: "Environment",
    ):
        super().__init__(scope, construct_id, env=env)

        iceberg_bucket = Bucket(self, "IcebergBucket")

        account_id = Stack.of(self).account
        region = Stack.of(self).region
        database = "demo"
        table = "nc_voter"

        iceberg_database = Database.from_database_arn(
            self,
            "IcebergDatabase",
            f"arn:aws:glue:{region}:{account_id}:database/{database}",
        )

        iceberg_table = Table.from_table_arn(
            self,
            "IcebergTable",
            f"arn:aws:glue:{region}:{account_id}:table/{database}/{table}",
        )

        pyiceberg_function = PyIcebergFunction(
            self, "PyIcebergFunction", iceberg_database, iceberg_table, iceberg_bucket
        )
