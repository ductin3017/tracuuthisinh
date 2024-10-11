from django.db import models
from .db_utils import get_neo4j_driver, get_mongodb_client

class Candidate(models.Model):
    candidate_id = models.CharField(max_length=50, primary_key=True)
    personal_info_id = models.CharField(max_length=50)

    def get_candidate_info(self):
        with get_neo4j_driver().session() as session:
            result = session.run(
                "MATCH (c:Candidate {candidate_id: $candidate_id}) RETURN c",
                candidate_id=self.candidate_id
            )
            record = result.single()
            if record:
                return dict(record['c'])
        return None

    def update_candidate_info(self, **kwargs):
        with get_neo4j_driver().session() as session:
            session.run(
                """
                MERGE (c:Candidate {candidate_id: $candidate_id})
                SET c += $properties
                """,
                candidate_id=self.candidate_id,
                properties=kwargs
            )

    def get_personal_info(self):
        mongo_client = get_mongodb_client()
        db = mongo_client.candidate
        return db.personal_info.find_one({"personal_info_id": self.personal_info_id})

    @classmethod
    def create_candidate(cls, candidate_id, personal_info_id, **kwargs):
        candidate = cls.objects.create(candidate_id=candidate_id, personal_info_id=personal_info_id)
        candidate.update_candidate_info(**kwargs)
        return candidate

class PersonalInfo(models.Model):
    personal_info_id = models.CharField(max_length=50, primary_key=True)
    date_of_birth = models.DateField()
    name = models.CharField(max_length=100)
    identity_number = models.CharField(max_length=20)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    gender = models.CharField(max_length=10)

    def get_personal_info(self):
        mongo_client = get_mongodb_client()
        db = mongo_client.candidate
        return db.personal_info.find_one({"personal_info_id": self.personal_info_id})

    def update_personal_info(self, **kwargs):
        mongo_client = get_mongodb_client()
        db = mongo_client.candidate
        db.personal_info.update_one(
            {"personal_info_id": self.personal_info_id},
            {"$set": kwargs},
            upsert=True
        )

    def validate_identity(self):
        # Căn cươc hợp lệ là phải có 12 số
        return len(self.identity_number) == 12 and self.identity_number.isdigit()

    @classmethod
    def create_personal_info(cls, **kwargs):
        personal_info = cls.objects.create(**kwargs)
        personal_info.update_personal_info(**kwargs)
        return personal_info