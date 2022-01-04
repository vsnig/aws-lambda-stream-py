from awslambdastream.utils.tags import adorn_standard_tags, env_tags


def test_adorn_standard_tags():
    uow = {"event": {"type": "thing-created"}}
    res = adorn_standard_tags("event")(uow)
    # print(res)
    assert res == {
        "event": {
            "type": "thing-created",
            "tags": {
                "account": "None",
                "region": "us-east-1",
                "stage": "None",
                "source": "None",
                "functionname": "None",
                "pipeline": "None",
            },
        }
    }


def test_env_tags_defaults():
    res = env_tags()

    assert res == {
        "account": "None",
        "region": "us-east-1",
        "stage": "None",
        "source": "None",
        "functionname": "None",
        "pipeline": "None",
    }


def test_env_tags_with_env_vars(monkeypatch):
    monkeypatch.setenv("ACCOUNT_NAME", "acct1")
    monkeypatch.setenv("STAGE", "test")
    monkeypatch.setenv("PROJECT", "proj1")
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "listener1")

    res = env_tags("p1")

    assert res == {
        "account": "acct1",
        "region": "us-east-1",
        "stage": "test",
        "source": "proj1",
        "functionname": "listener1",
        "pipeline": "p1",
    }
