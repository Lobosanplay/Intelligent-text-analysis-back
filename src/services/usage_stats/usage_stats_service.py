from config.supabase import supabase
from models.usage_stats.usage_stats_models import UsageStatsBase


class UsageStatsService:
    async def create(self, usageStatsData: UsageStatsBase) -> UsageStatsBase:
        response = (
            supabase.table("usage_stats")
            .insert(usageStatsData.model_dump(exclude_none=True))
            .execute()
        )

        if not response.data:
            raise Exception("Failed to create usage stats")

        return UsageStatsBase.model_validate(response.data[0])

    async def get_usage_by_user_id(self, user_id: str) -> UsageStatsBase:
        response = (
            supabase.table("usage_stats")
            .select("*")
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not response.data:
            raise Exception("Failed obtained user is stats")

        return UsageStatsBase.model_validate(response.data)

    async def increment_documents_stats_by_user_id(self, user_id: str):
        usage = await self.get_usage_by_user_id(user_id)

        response = (
            supabase.table("usage_stats")
            .update({"documents_uploaded": usage.documents_uploaded + 1})
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise Exception("Failed to update documents stats")

        return UsageStatsBase.model_validate(response.data[0])

    async def increment_usage_storage_by_user_id(self, user_id: str, size_mb: int):
        usage = await self.get_usage_by_user_id(user_id)

        response = (
            supabase.table("usage_stats")
            .update({"storage_used_mb": usage.storage_used_mb + size_mb})
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise Exception("Failed to update storage used stats")

        return UsageStatsBase.model_validate(response.data[0])

    async def increment_audio_minutes(self, user_id: str, minutes: int):
        usage = await self.get_usage_by_user_id(user_id)

        response = (
            supabase.table("usage_stats")
            .update(
                {"minutes_audio_processed": usage.minutes_audio_processed + minutes}
            )
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise Exception("Failed to increment audio minutes")

        return UsageStatsBase.model_validate(response.data[0])


usage_stats_service = UsageStatsService()
