from decimal import Decimal as D

from tests.factories import ProductFactory, ShopFactory, MeasurementUnitFactory


class ShopRecommendationTestCaseMixin:
    def setUp(self):
        self.unit_grams = MeasurementUnitFactory(name="grams")
        self.unit_liters = MeasurementUnitFactory(name="liters")
        self.expensive_bread_shop = ShopFactory()
        self.cheapest_bread_shop = ShopFactory()

        self._400gram_bread_kwargs = dict(name="bread", unit=self.unit_grams, unit_quantity=400)
        self._800gram_bread_kwargs = dict(name="bread", unit=self.unit_grams, unit_quantity=800)
        self._1liter_milk_kwargs = dict(name="milk", unit=self.unit_liters, unit_quantity=1)

        self.expensive_400gram_bread = ProductFactory(
            unit_price=D("50.00"), shop=self.expensive_bread_shop, **self._400gram_bread_kwargs
        )
        self.expensive_800gram_bread = ProductFactory(
            unit_price=D("90.00"), shop=self.expensive_bread_shop, **self._800gram_bread_kwargs
        )
        self.cheapest_400gram_bread = ProductFactory(
            unit_price=D("48.00"), shop=self.cheapest_bread_shop, **self._400gram_bread_kwargs
        )
        self.cheapest_800gram_bread = ProductFactory(
            unit_price=D("85.00"), shop=self.cheapest_bread_shop, **self._800gram_bread_kwargs
        )
