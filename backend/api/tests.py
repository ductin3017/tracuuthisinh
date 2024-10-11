from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Candidate, PersonalInfo
from .db_utils import get_neo4j_driver, get_mongodb_client

@override_settings(
    NEO4J_URI='bolt://localhost:7687',
    NEO4J_USERNAME='neo4j',
    NEO4J_PASSWORD='test_password',
    MONGODB_URI='mongodb://localhost:27017/test_candidate'
)
class CandidateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.candidate = Candidate.objects.create(
            candidate_id="C001",
            personal_info_id="P001"
        )
        self.neo4j_driver = get_neo4j_driver()
        self.mongo_client = get_mongodb_client()

    def test_get_candidate_info(self):
        with self.neo4j_driver.session() as session:
            session.run(
                "CREATE (c:Candidate {candidate_id: $candidate_id, name: $name})",
                candidate_id="C001", name="John Doe"
            )

        url = reverse('candidate-get-candidate-info', kwargs={'pk': 'C001'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "John Doe")

    def test_get_personal_info(self):
        db = self.mongo_client.candidate
        db.personal_info.insert_one({
            "personal_info_id": "P001",
            "name": "John Doe",
            "email": "john@example.com"
        })

        url = reverse('candidate-get-personal-info', kwargs={'pk': 'C001'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "John Doe")
        self.assertEqual(response.data['email'], "john@example.com")

    def tearDown(self):
        with self.neo4j_driver.session() as session:
            session.run("MATCH (c:Candidate) DELETE c")
        self.mongo_client.candidate.personal_info.delete_many({})

@override_settings(
    NEO4J_URI='bolt://localhost:7687',
    NEO4J_USERNAME='neo4j',
    NEO4J_PASSWORD='test_password',
    MONGODB_URI='mongodb://localhost:27017/test_candidate'
)
class PersonalInfoTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.personal_info = PersonalInfo.objects.create(
            personal_info_id="P001",
            date_of_birth="1990-01-01",
            name="John Doe",
            identity_number="123456789012",
            address="123 Main St",
            phone_number="1234567890",
            email="john@example.com",
            gender="Male"
        )

    def test_validate_identity(self):
        url = reverse('personalinfo-validate-identity', kwargs={'pk': 'P001'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_valid'])

    def test_invalid_identity(self):
        self.personal_info.identity_number = "123"  # Invalid number
        self.personal_info.save()
        url = reverse('personalinfo-validate-identity', kwargs={'pk': 'P001'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_valid'])
