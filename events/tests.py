from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from events.models import CustomAPIKey, Event, Stream


class MuxyAPITestCase(APITestCase):
    def authenticate_with_api_key(self, name=None, is_web=False, stream_key=None):
        _, key = self.create_api_key(name=name, is_web=is_web)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Api-Key {key}", HTTP_X_STREAM_KEY=stream_key
        )

    def create_api_key(self, name=None, is_web=False):
        return CustomAPIKey.objects.create_key(name=name or "test", is_web=is_web)


class EventTests(MuxyAPITestCase):
    def test_create_event(self):
        """Ensure we can create a new Event object"""
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
        """Ensure we can create a new Stream object for an exiting Event"""
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

    def test_create_stream_from_web_client(self):
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

    def test_delete_stream(self):
        """Ensure we can delete a Stream from an existing Event"""
        event = self.create_some_event()
        stream = self.create_some_stream(event)
        self.authenticate_with_api_key()
        response = self.client.delete(
            reverse("stream-detail", kwargs={"pk": stream.pk}), format="json"
        )

        # Assert response
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

        # Assert database
        self.assertEqual(Stream.objects.count(), 0)

    def test_delete_stream_from_web_client(self):
        """
        Ensure we can delete a Stream from an existing Event using a Web API key
        with the correct key.

        """
        event = self.create_some_event()
        stream = self.create_some_stream(event)
        self.authenticate_with_api_key(is_web=True, stream_key=stream.key)
        response = self.client.delete(
            reverse("stream-detail", kwargs={"pk": stream.pk}), format="json"
        )

        # Assert response
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

        # Assert database
        self.assertEqual(Stream.objects.count(), 0)

    def test_delete_stream_from_web_client_wrong_key(self):
        """
        Ensure we can delete a Stream from an existing Event using a Web API key
        with the correct key.

        """
        event = self.create_some_event()
        stream = self.create_some_stream(event)
        self.authenticate_with_api_key(is_web=True, stream_key="wrong_key")
        response = self.client.delete(
            reverse("stream-detail", kwargs={"pk": stream.pk}), format="json"
        )

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Assert database
        self.assertEqual(Stream.objects.count(), 1)

    def test_retrieve_stream(self):
        """Ensure we can retrieve a Stream from an existing Event"""
        event = self.create_some_event()
        stream = self.create_some_stream(event)
        self.authenticate_with_api_key()
        response = self.client.get(
            reverse("stream-detail", kwargs={"pk": stream.pk}), format="json"
        )

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data.get("publisher_name"), stream.publisher_name)
        self.assertTrue("key" in response.data)
        self.assertEqual(response.data.get("key"), stream.key)
        self.assertTrue("publisher_email" in response.data)
        self.assertEqual(response.data.get("publisher_email"), stream.publisher_email)

    def test_retrieve_stream_from_web_client_no_key(self):
        """
        Ensure we can retrieve a Stream from an existing Event using a Web API
        key and no streaming key.

        No private fields should be returned.

        """
        event = self.create_some_event()
        stream = self.create_some_stream(event)
        self.authenticate_with_api_key(is_web=True)
        response = self.client.get(
            reverse("stream-detail", kwargs={"pk": stream.pk}), format="json"
        )

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data.get("publisher_name"), stream.publisher_name)
        self.assertTrue("key" not in response.data)
        self.assertTrue("publisher_email" not in response.data)

    def test_update_stream_set_archive_urls(self):
        """
        Ensure we can update archive URLs for Stream.

        """
        event = self.create_some_event()
        stream = self.create_some_stream(event)
        self.authenticate_with_api_key(is_web=False)

        data = {
            "archive_urls": [
                { "url": "https://archive.org/foo", "name": "archive.org" },
                { "url": "https://youtube.com/foo", "name": "youtube.com" },
            ]
        }
        response = self.client.patch(
            reverse("stream-detail", kwargs={"pk": stream.pk}), data, format="json"
        )

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data.get("archive_urls"), data["archive_urls"])

        # Assert database
        self.assertEqual(stream.archive_urls.count(), 2)

    def create_some_event(self):
        starts_at = timezone.make_aware(datetime.today())
        ends_at = starts_at + timedelta(hours=2)

        return Event.objects.create(
            name="Solstice",
            url="https://solstice.com",
            starts_at=starts_at,
            ends_at=ends_at,
        )

    def create_some_stream(self, event):
        starts_at = event.starts_at
        ends_at = starts_at + timedelta(minutes=30)

        return Stream.objects.create(
            event=event,
            starts_at=starts_at,
            ends_at=ends_at,
            publisher_name="Performer #1",
            publisher_email="performer1@example.com",
        )
