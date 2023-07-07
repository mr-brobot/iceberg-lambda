from aws_cdk import App

from demo.stack import Stack
from demo.env import cloudbend_env

app = App()

Stack(app, "LambdaIcebergDemo", env=cloudbend_env)

app.synth()
