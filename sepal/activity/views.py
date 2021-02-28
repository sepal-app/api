from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status, Request

from sepal.auth import get_current_user
from sepal.organizations.lib import verify_org_id
from sepal.permissions import check_permission
from sepal.utils import create_schema, make_cursor_link

from .lib import ActivityPermission, get_activity

from .models import Activity
from .schema import ActivitySchema

router = APIRouter()


@router.get("", dependencies=[Depends(check_permission(ActivityPermission.Read))])
async def list(
    request: Request,
    response: Response,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
    cursor: Optional[str] = None,
    limit: int = 50,
    include: Optional[List["str"]] = Query(None),
) -> List[ActivitySchema]:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    activity = await get_activity(org_id, limit=limit, cursor=cursor, include=include)

    if len(activity) == limit:
        next_url = make_cursor_link(str(request.url), activity[-1].timestamp, limit)
        response.headers["Link"] = f"<{next_url}>; rel=next"

    return [ActivitySchema.from_orm(a) for a in activity]
