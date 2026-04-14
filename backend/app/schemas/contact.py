from pydantic import BaseModel


class ContactSubmission(BaseModel):
    company_name: str
    person_name: str
    email: str
    phone: str
    message: str


class ContactResponseData(BaseModel):
    sent: bool
    message: str


class ContactResponse(BaseModel):
    data: ContactResponseData


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
