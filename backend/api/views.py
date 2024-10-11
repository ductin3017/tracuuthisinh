from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Candidate, PersonalInfo
from .serializers import CandidateSerializer, PersonalInfoSerializer
from .db_utils import get_neo4j_driver, get_mongodb_client
import logging

logger = logging.getLogger(__name__)

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

    @action(detail=True, methods=['get'])
    def get_candidate_info(self, request, pk=None):
        candidate = self.get_object()
        try:
            with get_neo4j_driver().session() as session:
                result = session.run(
                    "MATCH (c:Candidate {candidate_id: $candidate_id}) RETURN c",
                    candidate_id=candidate.candidate_id
                )
                neo4j_data = result.single()
                if neo4j_data:
                    return Response(dict(neo4j_data['c']))
            return Response({"error": "Candidate not found in Neo4j"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching candidate info: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def get_personal_info(self, request, pk=None):
        candidate = self.get_object()
        try:
            mongo_client = get_mongodb_client()
            db = mongo_client.candidate
            personal_info = db.personal_info.find_one({"personal_info_id": candidate.personal_info_id})
            if personal_info:
                return Response(personal_info)
            return Response({"error": "Personal info not found in MongoDB"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching personal info: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PersonalInfoViewSet(viewsets.ModelViewSet):
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoSerializer

    def get_personal_info(self, request, pk=None):
        personal_info = self.get_object()
        mongo_client = get_mongodb_client()
        db = mongo_client.candidate
        mongo_data = db.personal_info.find_one({"personal_info_id": personal_info.personal_info_id})
        if mongo_data:
            return Response(mongo_data)
        return Response({"error": "Personal info not found in MongoDB"}, status=404)

    def update_personal_info(self, request, pk=None):
        personal_info = self.get_object()
        serializer = self.get_serializer(personal_info, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        mongo_client = get_mongodb_client()
        db = mongo_client.candidate
        db.personal_info.update_one(
            {"personal_info_id": personal_info.personal_info_id},
            {"$set": serializer.validated_data}
        )

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def validate_identity(self, request, pk=None):
        personal_info = self.get_object()
        # Implement identity validation logic here
        is_valid = True  # Replace with actual validation
        return Response({"is_valid": is_valid})
