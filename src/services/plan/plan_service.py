from config.supabase import supabase
from errors.domain_errors import PlanLimitExeceeded
from models.plan.plan_models import PlanBase
from models.usage_stats.usage_stats_models import UsageStatsBase


class PlanService:
    async def validate_document_upload(self, user_id: str, file_size_mb: float):
        plan = await self.get_user_plan(user_id)
        usage = await self.get_usage(user_id)

        if plan.max_documents and usage.documents_uploaded >= plan.max_documents:
            raise PlanLimitExeceeded("Document limit reached")

        if (
            plan.max_storage_mb
            and usage.storage_used_mb + file_size_mb > plan.max_storage_mb
        ):
            raise PlanLimitExeceeded("Storage limit exceeded")

    async def get_user_plan(self, user_id: str):
        response = (
            supabase.table("subscriptions")
            .select("plans(*)")
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not response.data:
            raise Exception("Failed to get user is plan")

        return PlanBase.model_validate(response.data["plans"])

    async def get_usage(self, user_id: str):
        response = (
            supabase.table("usage_stats")
            .select("*")
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not response.data:
            raise Exception("Failed to get user is usage")

        return UsageStatsBase.model_validate(response.data)


plan_service = PlanService()
