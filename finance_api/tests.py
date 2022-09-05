from django.test import TestCase
from .models import Animal

class AnimalTestCase(TestCase):
    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        Animal.objects.create(name="lion", sound="roar")
        Animal.objects.create(name="cat", sound="meow")
        lion = Animal.objects.get(name="lion")
        cat = Animal.objects.get(name="cat")
        self.assertEqual(cat.speak(), 'The cat says "meow"')
        self.assertEqual(lion.speak(), 'The lion says "roar"')
