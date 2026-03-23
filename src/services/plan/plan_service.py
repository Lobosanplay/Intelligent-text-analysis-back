from config.supabase import supabase
from errors.domain_errors import PlanLimitExeceeded
from models.plan.plan_models import PlanBase
from services.usage_stats.usage_stats_service import usage_stats_service


class PlanService:
    async def validate_document_upload(self, user_id: str, file_size_mb: float):
        plan = await self.get_user_plan(user_id)
        usage = await usage_stats_service.get_usage_by_user_id(user_id)

        if plan.max_documents and usage.documents_uploaded >= plan.max_documents:
            raise PlanLimitExeceeded("Document limit reached")

        if (
            plan.max_storage_mb
            and usage.monthly_storage_used_mb + file_size_mb > plan.max_storage_mb
        ):
            raise PlanLimitExeceeded("Storage limit exceeded")

    async def get_user_plan(self, user_id: str):
        sub = (
            supabase.table("subscriptions")
            .select("plan_id")
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not sub.data:
            raise Exception("No subscription found")

        plan = (
            supabase.table("plans")
            .select("*")
            .eq("id", sub.data["plan_id"])
            .single()
            .execute()
        )

        return PlanBase.model_validate(plan.data)


plan_service = PlanService()
