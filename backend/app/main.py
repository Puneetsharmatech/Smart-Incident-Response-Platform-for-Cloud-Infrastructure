# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json

# Firebase Imports
import firebase_admin
from firebase_admin import credentials, firestore, auth

# We will import monitoring inside the lifespan event to avoid circular dependency
# from app.api.v1 import monitoring # REMOVE THIS LINE

from app.config import settings

# Global variables (initialized within lifespan, but not directly imported by other modules)
_firestore_db_client = None
_firebase_auth_client = None
_current_app_id = None

# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _firestore_db_client, _firebase_auth_client, _current_app_id

    firebase_config_str = None
    initial_auth_token = None
    app_id_from_canvas = None

    if '__firebase_config' in globals() and globals()['__firebase_config']:
        firebase_config_str = globals()['__firebase_config']
        print("Firebase config found in Canvas globals.")
    else:
        print("Firebase config NOT found in Canvas globals. Using default/empty config.")

    if '__initial_auth_token' in globals() and globals()['__initial_auth_token']:
        initial_auth_token = globals()['__initial_auth_token']
        print("Initial auth token found in Canvas globals.")
    else:
        print("Initial auth token NOT found in Canvas globals. Will attempt anonymous sign-in.")

    if '__app_id' in globals() and globals()['__app_id']:
        app_id_from_canvas = globals()['__app_id']
        print(f"App ID found in Canvas globals: {app_id_from_canvas}")
    else:
        print("App ID NOT found in Canvas globals. Using default app ID.")
    
    _current_app_id = app_id_from_canvas if app_id_from_canvas else 'default-app-id'

    try:
        if firebase_config_str:
            cred = credentials.Certificate(json.loads(firebase_config_str))
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully with provided config.")
        else:
            print("Firebase Admin SDK not initialized with provided config. Check if __firebase_config is available.")

        _firestore_db_client = firestore.client()
        _firebase_auth_client = auth

        if initial_auth_token:
            # Firebase Admin SDK's auth.sign_in_with_custom_token is for server-side verification,
            # not for client-side authentication. We don't need to call it here to "authenticate" the SDK.
            # The SDK is authenticated via the service account credentials.
            # This line was conceptually incorrect for SDK authentication, but useful for understanding the token.
            print(f"Custom auth token provided: {initial_auth_token[:10]}...") # Just log its presence
        else:
            # The SDK doesn't "sign in anonymously" itself. Its operations are authorized by the service account.
            # This line for anonymous sign-in was also conceptually misplaced for SDK auth.
            print("No custom auth token provided. SDK operates via service account credentials.")

    except Exception as e:
        print(f"Failed to initialize Firebase Admin SDK: {e}")
        # In a real application, you might want to exit or disable Firebase features.

    # IMPORTANT: Import and include router AFTER Firebase is initialized and globals are set
    from app.api.v1 import monitoring # Import here
    app.include_router(monitoring.router, prefix="/api/v1") # Include here

    yield

    print("Application shutting down. Firebase cleanup (if any) here.")

# Dependency functions to provide Firestore client and app ID
def get_firestore_client():
    """Provides the Firestore client instance."""
    if _firestore_db_client is None:
        raise RuntimeError("Firestore client not initialized. Ensure FastAPI lifespan has run.")
    return _firestore_db_client

def get_app_id():
    """Provides the current application ID."""
    if _current_app_id is None:
        raise RuntimeError("App ID not initialized. Ensure FastAPI lifespan has run.")
    return _current_app_id

app = FastAPI(
    title="Smart Incident Response Backend",
    description="API for monitoring, incident detection, and response for cloud infrastructure.",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(monitoring.router, prefix="/api/v1") # REMOVED: Moved into lifespan

@app.get("/")
async def read_root():
    return {"message": "Welcome to Smart Incident Response Backend! Visit /docs for API documentation."}

