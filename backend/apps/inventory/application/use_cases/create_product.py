class CreateProduct:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, data):
        if data["price"] < 0:
            raise ValueError("Product price cannot be negative.")
        return self.repository.create(data)
