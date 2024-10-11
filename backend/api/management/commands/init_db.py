from django.core.management.base import BaseCommand
from api.db_utils import init_databases

class Command(BaseCommand):
    help = 'Initialize Neo4j constraints and MongoDB indexes'

    def handle(self, *args, **kwargs):
        init_databases()
        self.stdout.write(self.style.SUCCESS('Successfully initialized databases'))