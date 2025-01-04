from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from cache import redis_client
from database.repository import UserRepository
from schema.request import SignUpRequest, LogInRequest, VerifyOTPRequest, CreateOTPRequest
from schema.response import UserSchema, JWTResponse
from security import get_access_token
from service.user import UserService
from database.orm import User
router  = APIRouter(prefix="/users")


@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
        request: SignUpRequest,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends()
):
    # 1. request body(username, password)
    # 2. password -> hashing -> hashed_password
    #    aaa -> hash -> asgweraasd
    hash_password: str = user_service.hash_password(
        plain_password=request.password
    )

    # 3. User(username, hashed_password)
    user: User = User.create(
        username=request.username, password=hash_password
    )

    # 4. user -> db save
    user: User = user_repo.save_user(user=user)

    # 5. return user(id, username)
    return UserSchema.model_validate(user)

@router.post("/log-in")
def user_log_in_handler(
        request: LogInRequest,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends()
):
    #1. 리퀘스트바디로 유저네임과 패스워드를 입력받음
    #2. DB에서 유저정보를 읽어옴
    user: User | None = user_repo.get_user_by_username(
        username=request.username
    )
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    #3. 유저패스워스(해싱)에, 리퀘스트패스워드(일반)를 bcrypt.checkpw를 이용해서 검증
    verified: bool = user_service.verify_password(
        plain_password=request.password,
        hashed_password=user.password
    )
    if not verified:
        raise HTTPException(status_code=401, detail="Not Authorized")


    #4. create jwt
    access_token: str = user_service.create_jwt(username=user.username)


    #5. return jwt
    return JWTResponse(access_token=access_token)



@router.post("/email/otp")
def create_otp_handler(
    request: CreateOTPRequest,
    _: str = Depends(get_access_token),
    user_service: UserService = Depends(),
):
    otp: int = user_service.create_otp()
    redis_client.set(request.email, otp, ex=180)
    return {"otp": otp}

@router.post("/email/otp/verify")
def verify_otp_handler(
    request: VerifyOTPRequest,
    background_tasks: BackgroundTasks,
    access_token: str = Depends(get_access_token),
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
):
    otp: str = redis_client.get(request.email)
    if not otp:
        raise HTTPException(status_code=400, detail="Bad Request")
    if request.otp != int(otp):
        raise HTTPException(status_code=400, detail="Not Authorized")

    username: str = user_service.decode_jwt(access_token=access_token)
    user: User | None = user_repo.get_user_by_username(username=username)

    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    #save email to user
    background_tasks.add_task(
        user_service.send_email_to_user,
        email="aaa@aaa.aaa"
        )

    return UserSchema.model_validate(user)