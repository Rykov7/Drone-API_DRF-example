from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from drones.models import DroneCategory, Pilot
from drones import views, urls


class DroneCategoryTests(APITestCase):
    def post_drone_category(self, name):
        url = reverse(f'drones:{views.DroneCategoryList.name}')
        data = {'name': name}
        response = self.client.post(url, data, format='json')
        return response

    def test_post_and_get_drone_category(self):
        """
        Убеждаемся, что можем создать новый DroneCategory и потом получить его.
        """
        new_drone_category_name = 'Hexacopter'
        response = self.post_drone_category(new_drone_category_name)
        print(f"\nPK {DroneCategory.objects.get().pk}\n")
        assert response.status_code == status.HTTP_201_CREATED
        assert DroneCategory.objects.count() == 1
        assert DroneCategory.objects.get().name == new_drone_category_name

    def test_existing_drone_category_name(self):
        """
        Убедимся, что не можем создать DroneCategory с существующим именем.
        """
        new_drone_category_name = "Duplicated Copter"
        response1 = self.post_drone_category(new_drone_category_name)
        assert response1.status_code == status.HTTP_201_CREATED
        response2 = self.post_drone_category(new_drone_category_name)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        print(response2)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_drone_category_by_name(self):
        """
        Удостоверимся, что может фильтровать категории дронов по имени.
        """
        drone_category_name1 = 'Hexacopter'
        self.post_drone_category(drone_category_name1)
        drone_category_name2 = 'Octocopter'
        self.post_drone_category(drone_category_name2)
        filter_by_name = {'name': drone_category_name1}
        url = f'{reverse(urls.app_name + ":" + views.DroneCategoryList.name)}?{urlencode(filter_by_name)}'
        print(url)
        response = self.client.get(url, format='json')
        print(response)
        assert response.status_code == status.HTTP_200_OK
        # Убеждаемся, что получаем только один элемент в ответе.
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == drone_category_name1

    def test_get_drone_categories_collection(self):
        """
        Убедимся, что можем получить коллекцию категорий дронов.
        """
        new_drone_category_name = 'Super Copter'
        self.post_drone_category(new_drone_category_name)
        url = reverse(urls.app_name + ":" + views.DroneCategoryList.name)
        response = self.client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        # Убедимся, что можем получить только один элемент в ответе.
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == new_drone_category_name

    def test_update_drone_category(self):
        """
        Убедимся, что можем обновить одно поле у категории дронов.
        """
        drone_category_name = 'Category Initial Name'
        response = self.post_drone_category(drone_category_name)
        url = reverse(urls.app_name + ':' + views.DroneCategoryDetail.name, None, {response.data['pk']})
        updated_drone_category_name = 'Updated Name'
        data = {'name': updated_drone_category_name}
        patch_response = self.client.patch(url, data, format='json')
        assert patch_response.status_code == status.HTTP_200_OK
        assert patch_response.data['name'] == updated_drone_category_name

    def test_get_drone_category(self):
        """
        Убедимся, что можем получить одну категорию дронов оп id.
        """
        drone_category_name = 'Easy to retrieve'
        response = self.post_drone_category(drone_category_name)
        url = reverse(urls.app_name + ":" + views.DroneCategoryDetail.name, None, {response.data["pk"]})
        get_response = self.client.get(url, format='json')
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.data['name'] == drone_category_name


class PilotTests(APITestCase):
    def post_pilot(self, name, gender, races_count):
        url = reverse(urls.app_name + ':' + views.PilotList.name)
        print(url)
        data = {
            'name': name,
            'gender': gender,
            'races_count': races_count,
        }
        response = self.client.post(url, data, format='json')
        return response

    def create_user_and_set_token_credentials(self):
        user = User.objects.create_user('user01', 'user01@example.com', 'user01P4ssw0rD')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_post_and_get_pilot(self):
        """
        Убедимся, что можем создать нового Пилота и затем получить его.
        Убедимся, что не можем получить существующего пилота без токена.
        """
        self.create_user_and_set_token_credentials()
        new_pilot_name = "Sergei"
        new_pilot_gender = Pilot.MALE
        new_pilot_races_count = 5
        response = self.post_pilot(
            new_pilot_name,
            new_pilot_gender,
            new_pilot_races_count
        )
        print(f'\nPK {Pilot.objects.get().pk}')
        assert response.status_code == status.HTTP_201_CREATED
        assert Pilot.objects.count() == 1
        saved_pilot = Pilot.objects.get()
        assert saved_pilot.name == new_pilot_name
        assert saved_pilot.gender == new_pilot_gender
        assert saved_pilot.races_count == new_pilot_races_count
        url = reverse(urls.app_name + ':' + views.PilotDetail.name, None, {saved_pilot.pk})
        authorized_get_response = self.client.get(url, format='json')
        assert authorized_get_response.status_code == status.HTTP_200_OK
        assert authorized_get_response.data['name'] == new_pilot_name
        # Очистим данные авторизации.
        self.client.credentials()
        unauthorized_get_response = self.client.get(url, format='json')
        assert unauthorized_get_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_try_to_post_pilot_without_token(self):
        """
        Убедимся, что не можем создать пилота без токена.
        """
        new_pilot_name = 'Unauthorized Pilot'
        new_pilot_gender = Pilot.MALE
        new_pilot_race_count = 7
        response = self.post_pilot(
            new_pilot_name,
            new_pilot_gender,
            new_pilot_race_count
        )
        print(response)
        print(Pilot.objects.count())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Pilot.objects.count() == 0
