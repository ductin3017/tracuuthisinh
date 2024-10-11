import logging
from neo4j import GraphDatabase
from pymongo import MongoClient
from django.conf import settings

logger = logging.getLogger(__name__)

def get_neo4j_driver():
    try:
        return GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {str(e)}")
        raise

def get_mongodb_client():
    try:
        return MongoClient(settings.MONGODB_URI)
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

def create_neo4j_constraints():
    try:
        with get_neo4j_driver().session() as session:
            session.run("CREATE CONSTRAINT candidate_id IF NOT EXISTS FOR (c:Candidate) REQUIRE c.candidate_id IS UNIQUE")
        logger.info("Neo4j constraints created successfully")
    except Exception as e:
        logger.error(f"Failed to create Neo4j constraints: {str(e)}")
        raise

def create_mongodb_indexes():
    try:
        client = get_mongodb_client()
        db = client.candidate
        db.personal_info.create_index("personal_info_id", unique=True)
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create MongoDB indexes: {str(e)}")
        raise

def init_databases():
    create_neo4j_constraints()
    create_mongodb_indexes()
