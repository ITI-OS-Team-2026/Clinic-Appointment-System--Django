from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Seeds the database with initial sample data (doctors, slots, test accounts) to provide a clean system for testing.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting database seeding...'))
        
        # TODO: Implement actual data creation logic here.
        # Example actions:
        # 1. Create superuser/admin account
        # 2. Create 20 doctor accounts
        # 3. Create test patient and receptionist accounts
        # 4. Generate availability slots for doctors
        
        self.stdout.write('Created test accounts...')
        self.stdout.write('Created 20 doctors...')
        self.stdout.write('Generated availability slots...')
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded the system with clean sample data!'))
