from setuptools import setup, find_packages

# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
setup(
    name="awslambdastream",
    packages=find_packages(
      include=['aws_lambda_stream', 'aws_lambda_stream.*']),
    # pip install -e .
    install_requires=[
      "pytest==6.2.5",
      "pytest-mock==3.6.1",
      "pytest-cov==3.0.0",
      "boto3==1.18.64",
      "rx==3.2.0"
      ],
    # pip install -e .[dev]
    extras_require={
        'dev': [
          'flake8',
          'black'
        ],
    },
)