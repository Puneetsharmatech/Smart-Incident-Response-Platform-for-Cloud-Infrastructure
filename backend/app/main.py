# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json # Import json for parsing firebase_config_str

# Firebase Imports
import firebase_admin
from firebase_admin import credentials, firestore, auth

from app.api.v1 import monitoring
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
            user = await _firebase_auth_client.sign_in_with_custom_token(initial_auth_token)
            print(f"Firebase authenticated with custom token. User UID: {user.uid}")
        else:
            user = await _firebase_auth_client.sign_in_anonymously()
            print(f"Firebase authenticated anonymously. User UID: {user.uid}")

    except Exception as e:
        print(f"Failed to initialize or authenticate Firebase: {e}")

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

app.include_router(monitoring.router, prefix="/api/v1")

@app.get("/")
async def read_root():
    return {"message": "Welcome to Smart Incident Response Backend! Visit /docs for API documentation."}

