# File Sharing and Chat Application

This project is a file-sharing and chat application built using Python. It consists of a Flask server that handles user authentication, file uploads/downloads, and chat functionalities, along with a Tkinter-based desktop client that interacts with the server.

## Project Structure

```
file-sharing-chat-app
├── server
│   ├── app.py                # Entry point for the Flask server
│   ├── routes                 # Contains route definitions
│   │   ├── __init__.py       # Initializes the routes package
│   │   ├── auth.py           # User registration and login routes
│   │   ├── file.py           # File upload and download routes
│   │   └── chat.py           # Chat message handling routes
│   ├── models                 # Contains database models
│   │   ├── __init__.py       # Initializes the models package
│   │   └── user.py           # User model definition
│   ├── utils                  # Utility functions
│   │   ├── __init__.py       # Initializes the utils package
│   │   ├── encryption.py      # Functions for data encryption
│   │   └── validation.py      # Functions for input validation
│   ├── static                 # Static files (CSS, JS, images)
│   └── uploads                # Directory for uploaded files
├── client
│   ├── main.py                # Entry point for the Tkinter client
│   ├── filesharing.py         # Existing Tkinter GUI code
│   ├── gui                    # GUI components
│   │   ├── __init__.py       # Initializes the GUI package
│   │   ├── login.py           # Login window implementation
│   │   ├── chat.py            # Chat interface implementation
│   │   ├── file_upload.py      # File upload interface implementation
│   │   └── profile.py         # Profile management interface implementation
│   ├── utils                  # Client-side utility functions
│   │   ├── __init__.py       # Initializes the utils package
│   │   ├── api_requests.py    # Functions for HTTP requests to the server
│   │   └── encryption.py      # Functions for client-side data encryption
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd file-sharing-chat-app
   ```

2. **Install dependencies**:
   Create a virtual environment and install the required packages:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Run the Flask server**:
   Navigate to the `server` directory and run the server:
   ```
   cd server
   python app.py
   ```

4. **Run the Tkinter client**:
   Open a new terminal, navigate to the `client` directory, and run the client:
   ```
   cd client
   python main.py
   ```

## Usage

- **User Registration and Login**: Users can register and log in through the Tkinter client, which communicates with the Flask server for authentication.
- **File Upload and Download**: Users can upload files to the server and download files shared by others.
- **Chat Functionality**: Users can send and receive messages in real-time.

## Security

Ensure that sensitive data is encrypted both in transit and at rest. The application uses encryption utilities for secure data handling.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.