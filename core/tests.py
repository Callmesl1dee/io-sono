import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Table, Reservation
from .forms import UserRegistrationForm, ReservationForm

class ReservationTests(TestCase):
    def setUp(self):
        # Create and log in a test user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # Create a test table
        self.table = Table.objects.create(
            number="1",
            seats=4,
            pos_x=10,
            pos_y=15,
            is_active=True
        )
        self.reservation_url = reverse('core:reservation')
        self.slots_api_url = reverse('core:api_slots')

    def test_successful_reservation(self):
        """Test that booking an available table is successful."""
        data = {
            'name': 'Иван',
            'phone': '+79991234567',
            'date': '2026-06-20',
            'time': '10:00-12:00',
            'guests': 2,
            'table': self.table.id,
        }
        response = self.client.post(self.reservation_url, data)
        # Check that it redirects to profile
        self.assertRedirects(response, reverse('core:profile'))
        
        # Verify the reservation was created in the database
        self.assertEqual(Reservation.objects.count(), 1)
        res = Reservation.objects.first()
        self.assertEqual(res.name, 'Иван')
        self.assertEqual(res.table, self.table)
        self.assertEqual(res.date, datetime.date(2026, 6, 20))
        self.assertEqual(res.time, datetime.time(10, 0))
        self.assertEqual(res.user, self.user)

    def test_double_booking_prevention(self):
        """Test that booking the same table on the same date and time slot is prevented."""
        # Create first reservation
        Reservation.objects.create(
            name='Иван',
            phone='+79991234567',
            date='2026-06-20',
            time=datetime.time(10, 0),
            guests=2,
            table=self.table,
            status='confirmed'
        )
        
        # Try to book the same table on the same date and time
        data = {
            'name': 'Петр',
            'phone': '+79997654321',
            'date': '2026-06-20',
            'time': '10:00-12:00',
            'guests': 3,
            'table': self.table.id,
        }
        response = self.client.post(self.reservation_url, data)
        # It should NOT redirect, but render the reservation page again with status code 200
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservation.html')
        
        # Verify no second reservation was created
        self.assertEqual(Reservation.objects.count(), 1)
        
        # Verify that an error message is present
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('уже забронирован', messages[0].message)

    def test_slots_api_reflects_reservation(self):
        """Test that the slots API correctly shows slot availability."""
        # Check slots before booking (all should be free)
        response = self.client.get(self.slots_api_url, {'table': self.table.id, 'date': '2026-06-20'})
        self.assertEqual(response.status_code, 200)
        slots_data = response.json()
        
        # Find 10:00 slot
        slot_10 = next(s for s in slots_data if s['time'] == '10:00-12:00')
        self.assertFalse(slot_10['is_busy'])
        
        # Create a reservation for 10:00-12:00
        Reservation.objects.create(
            name='Иван',
            phone='+79991234567',
            date='2026-06-20',
            time=datetime.time(10, 0),
            guests=2,
            table=self.table,
            status='confirmed'
        )
        
        # Check slots after booking (10:00 slot should be busy)
        response = self.client.get(self.slots_api_url, {'table': self.table.id, 'date': '2026-06-20'})
        self.assertEqual(response.status_code, 200)
        slots_data = response.json()
        
        slot_10 = next(s for s in slots_data if s['time'] == '10:00-12:00')
        self.assertTrue(slot_10['is_busy'])

    def test_tables_status_api(self):
        """Test that the tables status API returns table as busy only when all slots are booked."""
        url = reverse('core:api_tables_status')
        date_str = '2026-06-20'
        
        # At first, it should be empty since no table has all slots booked
        response = self.client.get(url, {'date': date_str})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        
        # Book 5 out of 6 slots
        times = ["10:00", "12:00", "14:00", "16:00", "18:00"]
        for t in times:
            Reservation.objects.create(
                name='Иван',
                phone='+79991234567',
                date=date_str,
                time=datetime.time(int(t.split(':')[0]), 0),
                guests=2,
                table=self.table,
                status='confirmed'
            )
            
        # Still not completely busy (1 slot left)
        response = self.client.get(url, {'date': date_str})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        
        # Book the last slot ("20:00")
        Reservation.objects.create(
            name='Иван',
            phone='+79991234567',
            date=date_str,
            time=datetime.time(20, 0),
            guests=2,
            table=self.table,
            status='confirmed'
        )
        
        # Now it should be returned as busy
        response = self.client.get(url, {'date': date_str})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.table.id])

    def test_user_registration_form_valid(self):
        """Test that UserRegistrationForm is valid with correct data."""
        data = {
            'username': 'newuser',
            'email': 'new@user.com',
            'password': 'strongpassword123'
        }
        form = UserRegistrationForm(data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('strongpassword123'))

    def test_user_registration_form_invalid_username_exists(self):
        """Test that UserRegistrationForm is invalid when username already exists."""
        data = {
            'username': 'testuser',  # testuser was created in setUp
            'email': 'different@user.com',
            'password': 'somepassword'
        }
        form = UserRegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_reservation_form_validation(self):
        """Test that ReservationForm handles time formatting correctly."""
        data = {
            'name': 'Иван',
            'phone': '+79991234567',
            'date': '2026-06-20',
            'time': '10:00-12:00',
            'guests': 2,
            'table': self.table.id
        }
        form = ReservationForm(data)
        self.assertTrue(form.is_valid())
        reservation = form.save(commit=False)
        self.assertEqual(reservation.time, datetime.time(10, 0))

    def test_reservation_model_clean_validation(self):
        """Test that Reservation model clean() validation raises ValidationError directly on conflicts."""
        # Create first booking
        Reservation.objects.create(
            name='Иван',
            phone='+79991234567',
            date='2026-06-20',
            time=datetime.time(10, 0),
            guests=2,
            table=self.table,
            status='confirmed'
        )

        # Build second conflicting booking
        conflict_res = Reservation(
            name='Петр',
            phone='+79997654321',
            date='2026-06-20',
            time=datetime.time(10, 0),
            guests=3,
            table=self.table
        )

        # Verify full_clean / clean raises ValidationError
        with self.assertRaises(ValidationError):
            conflict_res.full_clean()

        with self.assertRaises(ValidationError):
            conflict_res.save()

    def test_loyalty_accrual_confirmed_reservations(self):
        """Test that user loyalty bonus points accrue only for confirmed reservations."""
        # Check initial points (0)
        self.assertEqual(self.user.profile.bonus_points, 0)

        # Create one confirmed and one pending reservation
        Reservation.objects.create(
            name='Иван',
            phone='+79991234567',
            date='2026-06-20',
            time=datetime.time(10, 0),
            guests=2,
            table=self.table,
            user=self.user,
            status='confirmed'
        )
        Reservation.objects.create(
            name='Иван',
            phone='+79991234567',
            date='2026-06-20',
            time=datetime.time(12, 0),
            guests=2,
            table=self.table,
            user=self.user,
            status='pending'
        )

        # Trigger points sync by fetching profile page
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.status_code, 200)

        # Verify points (1 confirmed booking * 100 = 100 points)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bonus_points, 100)

    def test_tables_api(self):
        """Test that tables API returns the active tables list with pos_x/pos_y coordinates."""
        url = reverse('core:api_tables')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        tables_data = response.json()
        self.assertEqual(len(tables_data), 1)
        self.assertEqual(tables_data[0]['number'], '1')
        self.assertEqual(tables_data[0]['x'], 10)
        self.assertEqual(tables_data[0]['y'], 15)
