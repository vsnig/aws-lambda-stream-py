import os


def adorn_standard_tags(event_field):
    def _adorn_standard_tags(uow):
        return {
            **uow,
            event_field: {
                **uow[event_field],
                "tags": {
                    **env_tags(uow.get("pipeline")),
                    # **skip_tag(), # add `skip: true` for testing, not implemented for now
                    **uow[event_field].get("tags", {}),
                },
            },
        }

    return _adorn_standard_tags


def env_tags(pipeline=None):
    return {
        "account": os.environ.get("ACCOUNT_NAME", "None"),
        "region": os.environ.get("AWS_REGION", "None"),
        "stage": os.environ.get("STAGE") or os.environ.get("SERVERLESS_STAGE", "None"),
        "source": os.environ.get("PROJECT", "None")
        or os.environ.get("SERVERLESS_PROJECT", "None"),
        "functionname": os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "None"),
        "pipeline": pipeline or "None",
    }
