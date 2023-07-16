from attrs import define


@define
class Flower:
    name: str
    count: int
    cost: int
    id: int = 0


class FlowersRepository:
    flowers: list[Flower]

    def __init__(self):
        self.flowers = []

    # необходимые методы сюда
    def get_all_flowers(self):
        return self.flowers

    def save(self,flower):
        flower.id = len(self.flowers)+1
        self.flowers.insert(0,flower)
    def delete_flower(self,flower_id):
        for i,f in enumerate(self.flowers):
            if f.id == flower_id:
                del self.flowers[i]
                return True
        return False
    def get_one(self,flower_id):
        for i,f in enumerate(self.flowers):
            if f.id == flower_id:
                return self.flowers[i]
        return None
    def get_many(self,flower_ids):
        flowers = []
        for i,f in enumerate(self.flowers):
            if str(f.id) in [i for i in flower_ids]:
                flowers.append(f)
        return flowers
    # конец решения
