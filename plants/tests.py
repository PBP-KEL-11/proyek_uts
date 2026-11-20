from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import GardenPlant, Plant


class PlantAPITestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="testpass123",
        )
        self.plant = Plant.objects.create(
            species_id=1,
            common_name="Basil",
            scientific_name="Ocimum basilicum",
            watering="average",
            watering_days=3,
            sunlight="full_sun",
        )

    def test_catalog_is_public_but_writes_require_auth(self):
        response = self.client.get(reverse("plant-api-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.post(
            reverse("plant-api-list"),
            {"species_id": 2, "common_name": "Mint"},
            format="json",
        )
        self.assertIn(response.status_code, (401, 403))

        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("plant-api-list"),
            {"species_id": 2, "common_name": "Mint"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["common_name"], "Mint")

    def test_catalog_crud(self):
        self.client.force_authenticate(self.user)
        url = reverse("plant-api-detail", args=[self.plant.id])

        response = self.client.patch(url, {"watering_days": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plant.refresh_from_db()
        self.assertEqual(self.plant.watering_days, 5)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Plant.objects.filter(id=self.plant.id).exists())

    def test_cannot_delete_catalog_plant_used_by_garden(self):
        GardenPlant.objects.create(user=self.user, plant=self.plant)

        self.client.force_authenticate(self.user)
        response = self.client.delete(
            reverse("plant-api-detail", args=[self.plant.id])
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Plant.objects.filter(id=self.plant.id).exists())

    def test_garden_requires_authentication(self):
        response = self.client.get(reverse("garden-plant-api-list"))
        self.assertIn(response.status_code, (401, 403))

    def test_garden_is_isolated_per_user(self):
        own = GardenPlant.objects.create(user=self.user, plant=self.plant)
        GardenPlant.objects.create(user=self.other_user, plant=self.plant)

        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("garden-plant-api-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own.id)

        response = self.client.get(
            reverse("garden-plant-api-detail", args=[own.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["plant_detail"]["common_name"], "Basil")
        self.assertIn("next_watering", response.data)
        self.assertIn("needs_water", response.data)

    def test_create_garden_plant_sets_user_and_rejects_duplicate(self):
        self.client.force_authenticate(self.user)
        url = reverse("garden-plant-api-list")

        response = self.client.post(url, {"plant": self.plant.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GardenPlant.objects.get().user, self.user)

        response = self.client.post(url, {"plant": self.plant.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("plant", response.data)

    def test_cannot_read_other_users_garden_plant(self):
        other = GardenPlant.objects.create(user=self.other_user, plant=self.plant)

        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse("garden-plant-api-detail", args=[other.id])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
