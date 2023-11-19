import ray
import time


ray.init(
    num_cpus=4,
)


@ray.remote
def tardo_5_segundos(name: str, actorRef: Actor):
    time.sleep(5)
    actorRef.inc.remote()
    return f"{name} tardo 5 segundos"


@ray.actor
class Actor:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

    def log(self):
        print(self.count)
    

actor = Actor.remote()

actor.inc.remote()



results = []

for i in range(4):
    results.append(tardo_5_segundos.remote("resultado " + str(i), actor))


print(ray.get(results))
