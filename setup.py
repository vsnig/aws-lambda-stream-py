from setuptools import setup, find_packages

# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
setup(
    name="awslambdastream",
    packages=find_packages(include=['aws_lambda_stream', 'aws_lambda_stream.*']),  # __init__.py folders search
    # package_data={'twclf.training': ['data/*']},
    install_requires=[
      "pytest==6.2.5",
      "pytest-mock==3.6.1",
      "pytest-cov==3.0.0",
      "boto3==1.18.64",
      "rx==3.2.0"
      ], #  pip install -e .
    # extras_require={  # pip install -e .[interactive] -- on local machine to train, won't be installed in CiCd
    #     'local': ['jupyter'],
    # },
    # entry_points={
    #     'console_scripts': ['retrain=twclf.training:main'] #todo: modify to retrain classifier
    # },
)