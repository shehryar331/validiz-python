from typing import List, Optional

from pydantic import BaseModel


class EmailResponse(BaseModel):
    email: str
    is_valid: bool
    error_message: Optional[str] = None

    # Additional fields requested by user
    status: Optional[str] = None
    sub_status: Optional[str] = None
    free_email: Optional[bool] = None
    account: Optional[str] = None
    domain: Optional[str] = None
    smtp_provider: Optional[str] = None
    mx_found: Optional[bool] = None
    mx_record: Optional[List[str]] = None
