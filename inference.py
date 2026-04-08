import os
from app import app, init_db

if __name__ == "__main__":
    # Ensure database is initialized
    init_db()
    
    # Run the Flask app on port 5000 and bind to all interfaces
    # OpenEnv normally looks for services running on a specific port or executes this script
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
