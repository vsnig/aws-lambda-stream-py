import rx 
from rx import operators as ops
from rx.scheduler.threadpoolscheduler import ThreadPoolScheduler

pool_scheduler = ThreadPoolScheduler(2)

def my_op(obv):
  return rx.pipe(
    ops.map(lambda x: x),
    ops.flat_map(lambda batch_uow: rx.just(batch_uow).pipe(
        ops.subscribe_on(pool_scheduler),
        ops.map(lambda x: x.upper()),
      )),
    ops.to_list(),
  )(obv)

def test_my_op():
  collected = []
  
  def on_next(x):
    print('on_next', x)
    collected.append(x)

  res = my_op(rx.from_(["a", "b", "c"])).run()
  
  
  print("res::", res)
  # my_op(rx.from_(["a", "b", "c"])).subscribe(
  #   on_next=on_next,
  #   on_error=lambda e: print("error::", e),
  #   on_completed=lambda: print("completed")
  # )

  # pool_scheduler.executor.shutdown()

  # print("collected: ", collected)