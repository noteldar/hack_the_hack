from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_refresh_token
from app.schemas.auth import Token
from app.auth.oauth import google_oauth, microsoft_oauth, authenticate_oauth_user

router = APIRouter()


@router.get("/google")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    redirect_uri = request.url_for('google_callback')
    return await google_oauth.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        token = await google_oauth.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            user_info = await google_oauth.get_userinfo(token)

        # Authenticate user
        auth_token = await authenticate_oauth_user('google', user_info, db)

        # In a real app, you'd redirect to frontend with token
        return auth_token

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth failed: {str(e)}"
        )


@router.get("/microsoft")
async def microsoft_login(request: Request):
    """Initiate Microsoft OAuth login"""
    redirect_uri = request.url_for('microsoft_callback')
    return await microsoft_oauth.authorize_redirect(request, redirect_uri)


@router.get("/microsoft/callback")
async def microsoft_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Microsoft OAuth callback"""
    try:
        token = await microsoft_oauth.authorize_access_token(request)
        user_info = await microsoft_oauth.get_userinfo(token)

        # Authenticate user
        auth_token = await authenticate_oauth_user('microsoft', user_info, db)

        # In a real app, you'd redirect to frontend with token
        return auth_token

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Microsoft OAuth failed: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token"""
    user_id = verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = create_access_token(subject=user_id)
    new_refresh_token = create_refresh_token(subject=user_id)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
async def logout():
    """Logout user (client should remove tokens)"""
    return {"message": "Successfully logged out"}