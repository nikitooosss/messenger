import pytest

from backend.services.core.jwt import create_access_token, get_jwt_payload
from backend.services.jwt import JWTService
from backend.services.schemas.jwt import Token, TokenData


class TestJWTService:
    @pytest.mark.asyncio
    async def test_get_access_token_returns_token(self, jwt_service: JWTService):
        data = TokenData(id=1, uniq_name="testuser")
        token = await jwt_service.get_access_token(data=data)

        assert isinstance(token, Token)
        assert token.token_type == "bearer"
        assert isinstance(token.access_token, str)
        assert len(token.access_token) > 0

    @pytest.mark.asyncio
    async def test_get_access_token_contains_valid_payload(
        self, jwt_service: JWTService
    ):
        data = TokenData(id=42, uniq_name="johndoe")
        token = await jwt_service.get_access_token(data=data)

        payload = get_jwt_payload(token.access_token)
        assert payload is not None
        assert payload.id == 42
        assert payload.uniq_name == "johndoe"

    @pytest.mark.asyncio
    async def test_get_access_token_with_uniq_name(self, jwt_service: JWTService):
        data = TokenData(id=99, uniq_name="someuser")
        token = await jwt_service.get_access_token(data=data)

        payload = get_jwt_payload(token.access_token)
        assert payload is not None
        assert payload.id == 99
        assert payload.uniq_name == "someuser"

    @pytest.mark.asyncio
    async def test_get_access_token_same_data_produces_different_tokens_due_to_exp(
        self, jwt_service: JWTService
    ):
        import asyncio

        data = TokenData(id=1, uniq_name="testuser")
        token1 = await jwt_service.get_access_token(data=data)
        await asyncio.sleep(1.1)
        token2 = await jwt_service.get_access_token(data=data)

        assert token1.access_token != token2.access_token


class TestCoreJWT:
    def test_create_and_decode_token(self):
        data = {"id": 1, "uniq_name": "testuser"}
        token = create_access_token(data=data)

        payload = get_jwt_payload(token)
        assert payload is not None
        assert payload.id == 1
        assert payload.uniq_name == "testuser"

    def test_invalid_token_returns_none(self):
        payload = get_jwt_payload("invalid.token.here")
        assert payload is None
