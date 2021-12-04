from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone

from events.models import Event, Stream, CustomAPIKey
from datetime import datetime, timedelta


class MuxyAPITestCase(APITestCase):
    def authenticate_with_api_key(self, name=None, is_web=False):
        _, key = self.create_api_key(name=name, is_web=is_web)
        self.client.credentials(HTTP_AUTHORIZATION=f"Api-Key {key}")

    def create_api_key(self, name=None, is_web=False):
        return CustomAPIKey.objects.create_key(name=name or "test", is_web=is_web)


class EventTests(MuxyAPITestCase):
    def test_create_event(self):
        """
        Ensure we can create a new Event object

        """
        url = reverse("event-list")

        starts_at = timezone.make_aware(datetime.today())
        ends_at = starts_at + timedelta(hours=2)

        data = {
            "name": "Solstice",
            "event_url": "https://solstice.com",
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
        }
        self.authenticate_with_api_key()
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().name, "Solstice")


class StreamTests(MuxyAPITestCase):
    def test_create_stream(self):
        """
        Ensure we can create a new Stream object for an exiting Event

        """
        # Build parameters
        event = self.create_some_event()
        event_url = reverse("event-detail", kwargs={"pk": event.pk})
        starts_at = event.starts_at
        ends_at = starts_at + timedelta(minutes=30)
        data = {
            "publisher_name": "Performer #1",
            "publisher_email": "performer@example.com",
            "event": event_url,
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
        }
        self.authenticate_with_api_key()
        response = self.client.post(reverse("stream-list"), data, format="json")

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertIsNotNone(response.data.get("key"))

        # Assert database
        self.assertEqual(Stream.objects.count(), 1)
        stream = Stream.objects.get()
        self.assertEqual(stream.publisher_name, "Performer #1")
        self.assertEqual(stream.event, event)

    def test_create_stream_web_client(self):
        """
        Ensure we can create a new Stream object for an exiting Event using a
        Web API key

        """
        # Build parameters
        event = self.create_some_event()
        event_url = reverse("event-detail", kwargs={"pk": event.pk})
        starts_at = event.starts_at
        ends_at = starts_at + timedelta(minutes=30)
        data = {
            "publisher_name": "Performer #1",
            "publisher_email": "performer@example.com",
            "event": event_url,
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
        }
        self.authenticate_with_api_key(is_web=True)
        response = self.client.post(reverse("stream-list"), data, format="json")

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertIsNotNone(response.data.get("key"))

        # Assert database
        self.assertEqual(Stream.objects.count(), 1)
        stream = Stream.objects.get()
        self.assertEqual(stream.publisher_name, "Performer #1")
        self.assertEqual(stream.event, event)

    def create_some_event(self):
        starts_at = timezone.make_aware(datetime.today())
        ends_at = starts_at + timedelta(hours=2)

        return Event.objects.create(
            name="Solstice",
            url="https://solstice.com",
            starts_at=starts_at,
            ends_at=ends_at,
        )
