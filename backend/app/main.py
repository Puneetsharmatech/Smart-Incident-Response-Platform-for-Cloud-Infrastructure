# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json

# Firebase Imports
import firebase_admin
from firebase_admin import credentials, firestore # Removed 'auth' import

# Global variables (initialized within lifespan, but not directly imported by other modules)
_firestore_db_client = None
_current_app_id = None

# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _firestore_db_client, _current_app_id

    firebase_config_str = None
    app_id_from_canvas = None

    # Check if __firebase_config is defined (provided by Canvas)
    if '__firebase_config' in globals() and globals()['__firebase_config']:
        firebase_config_str = globals()['__firebase_config']
        print("Firebase config found in Canvas globals.")
    else:
        print("Firebase config NOT found in Canvas globals. Firebase Admin SDK will NOT be initialized.")

    # Check if __app_id is defined (provided by Canvas)
    if '__app_id' in globals() and globals()['__app_id']:
        app_id_from_canvas = globals()['__app_id']
        print(f"App ID found in Canvas globals: {app_id_from_canvas}")
    else:
        print("App ID NOT found in Canvas globals. Using default app ID for collection path.")
    
    _current_app_id = app_id_from_canvas if app_id_from_canvas else 'default-app-id'

    try:
        if firebase_config_str:
            # Attempt to parse and initialize Firebase Admin SDK
            try:
                cred = credentials.Certificate(json.loads(firebase_config_str))
                firebase_admin.initialize_app(cred)
                _firestore_db_client = firestore.client()
                print("Firebase Admin SDK initialized and Firestore client obtained successfully.")
            except json.JSONDecodeError:
                print("Error: __firebase_config is not valid JSON. Firebase Admin SDK NOT initialized.")
            except Exception as e:
                print(f"Failed to initialize Firebase Admin SDK with provided config: {e}")
        else:
            print("Firebase Admin SDK not initialized (no config provided). Firestore operations will fail.")

    except Exception as e:
        print(f"An unexpected error occurred during Firebase setup: {e}")

    # IMPORTANT: Import and include router AFTER Firebase setup attempts are complete
    from app.api.v1 import monitoring # Import here
    app.include_router(monitoring.router, prefix="/api/v1") # Include here

    yield

    print("Application shutting down. Firebase cleanup (if any) here.")

# Dependency functions to provide Firestore client and app ID
def get_firestore_client():
    """Provides the Firestore client instance."""
    if _firestore_db_client is None:
        raise RuntimeError("Firestore client not initialized. This typically happens if __firebase_config was not provided by the environment, or if initialization failed. Incidents will not be saved/retrieved.")
    return _firestore_db_client

def get_app_id():
    """Provides the current application ID."""
    if _current_app_id is None:
        # This should ideally not happen if app_id is set to 'default-app-id' as fallback
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

@app.get("/")
async def read_root():
    return {"message": "Welcome to Smart Incident Response Backend! Visit /docs for API documentation."}

