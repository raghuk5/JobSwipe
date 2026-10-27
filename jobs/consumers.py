from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from .models import CompanyMembership, Conversation, JobSwipe, Message


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"][
            "conversation_id"
        ]
        self.group_name = f"conversation_{self.conversation_id}"

        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close(code=4401)
            return

        if not await self.can_access_conversation(
            user.pk, self.conversation_id
        ):
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(
            self.group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name, self.channel_name
            )

    async def receive_json(self, content, **kwargs):
        if content.get("type") != "chat.message":
            return

        body = content.get("body", "")
        if not isinstance(body, str):
            return

        body = body.strip()
        if not body:
            await self.send_json({"type": "chat.error", "message": "Message cannot be empty."})
            return

        if len(body) > 4000:
            await self.send_json({"type": "chat.error", "message": "Message must be 4000 characters or fewer."})
            return

        user = self.scope["user"]

        # Recheck permissions before saving every message.
        if not await self.can_access_conversation(
            user.pk, self.conversation_id
        ):
            await self.close(code=4403)
            return

        message_data = await self.save_message(
            user.pk, self.conversation_id, body
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                **message_data,
            },
        )

    async def chat_message(self, event):
        await self.send_json({
            "type": "chat.message",
            "id": event["id"],
            "body": event["body"],
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"],
            "created_at": event["created_at"],
        })

    @database_sync_to_async
    def can_access_conversation(self, user_id, conversation_id):
        conversation = (
            Conversation.objects
            .select_related("swipe", "swipe__job")
            .filter(
                pk=conversation_id,
                swipe__interest_status=JobSwipe.InterestStatus.ACCEPTED,
            )
            .first()
        )

        if conversation is None:
            return False

        if conversation.swipe.user_id == user_id:
            return True

        return CompanyMembership.objects.filter(
            user_id=user_id,
            company_id=conversation.swipe.job.company_id,
            is_active=True,
        ).exists()

    @database_sync_to_async
    def save_message(self, user_id, conversation_id, body):
        message = Message.objects.create(
            conversation_id=conversation_id,
            sender_id=user_id,
            body=body,
        )

        Conversation.objects.filter(
            pk=conversation_id
        ).update(updated_at=timezone.now())

        return {
            "id": message.pk,
            "body": message.body,
            "sender_id": message.sender_id,
            "sender_name": (
                message.sender.full_name or message.sender.email
            ),
            "created_at": timezone.localtime(
                message.created_at
            ).strftime("%d %b %Y, %H:%M"),
        }
