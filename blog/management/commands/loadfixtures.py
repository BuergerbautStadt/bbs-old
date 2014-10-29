from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Sets up data for the project's blog"

    def handle(self, *args, **options):

        
        call_command("loaddata", "wagtailcore.json")        
        call_command("loaddata", "blog.json")
        
        self.stdout.write('Fertig')
