from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    Schema para la respuesta del token JWT
    """
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")


class TokenData(BaseModel):
    """
    Schema para los datos contenidos en el token JWT
    """
    username: str | None = None


class LoginRequest(BaseModel):
    """
    Schema para la petición de login
    """
    username: str = Field(..., description="Nombre de usuario")
    password: str = Field(..., description="Contraseña")