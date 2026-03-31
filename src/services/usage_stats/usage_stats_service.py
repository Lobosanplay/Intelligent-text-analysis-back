from config.supabase import supabase
from models.usage_stats.usage_stats_models import UsageStatsBase


class UsageStatsService:
    async def create_ussage_stats(
        self, usageStatsData: UsageStatsBase
    ) -> UsageStatsBase:
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

    async def increment_user_stats_by_id(
        self, user_id: str, size_mb: float, minutes: int
    ):
        supabase.rpc(
            "increment_usage",
            {
                "p_user_id": user_id,
                "p_documents": 1,
                "p_monthly_storage_used_mb": size_mb,
                "p_total_storage_mb": size_mb,
                "p_audio_minutes": minutes,
            },
        ).execute()

    async def deleted_file_by_user_id(self, user_id: str, size_mb: float):
        supabase.rpc(
            "increment_usage", {"p_user_id": user_id, "p_total_storage_mb": -size_mb}
        ).execute()


usage_stats_service = UsageStatsService()
