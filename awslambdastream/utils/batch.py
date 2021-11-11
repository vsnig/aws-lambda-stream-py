def to_batch_uow(batch):
    return {"batch": batch}


# use with flat_map
def unbatch_uow(uow):
    outer_uow_minus_batch = {**uow}
    batch = outer_uow_minus_batch.pop("batch")

    return [
        {
            **inner_uow_from_batch,
            **outer_uow_minus_batch,
        }
        for inner_uow_from_batch in batch
    ]
