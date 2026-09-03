class ChangeProductPrice:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, product_id, new_price):
        if new_price < 0:
            raise ValueError("Product price cannot be negative.")
        return self.repository.change_price(product_id, new_price)
