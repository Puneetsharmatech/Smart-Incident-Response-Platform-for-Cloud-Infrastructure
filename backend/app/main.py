# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager # For FastAPI's lifespan events

from app.api.v1 import monitoring
from app.config import settings

# Firebase Imports
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Global variables for Firebase (will be initialized in lifespan event)
db = None
firebase_auth = None
current_app_id = None # To store __app_id

# Lifespan context manager for FastAPI
# This allows us to run code when the application starts up and shuts down.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Event ---
    global db, firebase_auth, current_app_id # Declare globals to modify them

    # Access Canvas-provided global variables
    firebase_config_str = None
    initial_auth_token = None
    app_id_from_canvas = None

    # Check if __firebase_config is defined (provided by Canvas)
    if '__firebase_config' in globals() and globals()['__firebase_config']:
        firebase_config_str = globals()['__firebase_config']
        print("Firebase config found in Canvas globals.")
    else:
        print("Firebase config NOT found in Canvas globals. Using default/empty config.")

    # Check if __initial_auth_token is defined (provided by Canvas)
    if '__initial_auth_token' in globals() and globals()['__initial_auth_token']:
        initial_auth_token = globals()['__initial_auth_token']
        print("Initial auth token found in Canvas globals.")
    else:
        print("Initial auth token NOT found in Canvas globals. Will attempt anonymous sign-in.")

    # Check if __app_id is defined (provided by Canvas)
    if '__app_id' in globals() and globals()['__app_id']:
        app_id_from_canvas = globals()['__app_id']
        print(f"App ID found in Canvas globals: {app_id_from_canvas}")
    else:
        print("App ID NOT found in Canvas globals. Using default app ID.")
    
    current_app_id = app_id_from_canvas if app_id_from_canvas else 'default-app-id'


    try:
        # Initialize Firebase Admin SDK
        # The firebase_config_str contains the necessary project ID, etc.
        if firebase_config_str:
            cred = credentials.Certificate(json.loads(firebase_config_str))
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully with provided config.")
        else:
            # Fallback for local testing without Canvas globals (e.g., if you run uvicorn directly)
            # For local testing, you might need a service account key file or use GOOGLE_APPLICATION_CREDENTIALS
            # For this project, we primarily rely on Canvas's provided config.
            print("Firebase Admin SDK not initialized with provided config. Check if __firebase_config is available.")
            # If running locally and need Firebase, set GOOGLE_APPLICATION_CREDENTIALS env var
            # or provide a path to a service account key JSON.
            # For now, we'll proceed, but Firestore operations will fail without proper init.

        db = firestore.client()
        firebase_auth = auth

        # Authenticate with the provided custom token or anonymously
        if initial_auth_token:
            user = await firebase_auth.sign_in_with_custom_token(initial_auth_token)
            print(f"Firebase authenticated with custom token. User UID: {user.uid}")
        else:
            # If no custom token, sign in anonymously (for basic access if rules allow)
            user = await firebase_auth.sign_in_anonymously()
            print(f"Firebase authenticated anonymously. User UID: {user.uid}")

    except Exception as e:
        print(f"Failed to initialize or authenticate Firebase: {e}")
        # In a real application, you might want to exit or disable Firebase features.

    yield # This yields control to the FastAPI application to handle requests

    # --- Shutdown Event (optional, for cleanup) ---
    print("Application shutting down. Firebase cleanup (if any) here.")


# Initialize the FastAPI application with the lifespan context manager.
app = FastAPI(
    title="Smart Incident Response Backend",
    description="API for monitoring, incident detection, and response for cloud infrastructure.",
    version="0.1.0",
    lifespan=lifespan # Attach the lifespan event handler
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

