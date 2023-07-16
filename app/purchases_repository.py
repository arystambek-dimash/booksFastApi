from attrs import define


@define
class Purchase:
    user_id: int = 0
    flower_id: int = 0


class PurchasesRepository:
    purchases: list[Purchase]

    def __init__(self):
        self.purchases = []

    def get_all_purchased(self, user_id):
        purchases_by_user = []
        for purchase in self.purchases:
            if user_id == purchase.user_id:
                purchases_by_user.append(purchase)
        return purchases_by_user

    def save_purchased(self,purchased):
        self.purchases.append(purchased)


