from aws_cdk import App

from demo.stack import Demo
from demo.env import cloudbend_env

app = App()

Demo(app, "LambdaIcebergDemo", env=cloudbend_env)

app.synth()
