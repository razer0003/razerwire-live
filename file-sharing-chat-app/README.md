# File Sharing and Chat Application

This project is a file-sharing and chat application that consists of a Flask server for handling backend operations and a Tkinter-based desktop client for user interaction. The application allows users to register, log in, upload and download files, and send chat messages securely.

## Project Structure

```
file-sharing-chat-app
├── server
│   ├── app.py                # Entry point for the Flask server
│   ├── models                # Contains data models
│   │   ├── __init__.py       # Initializes models package
│   │   └── user.py           # User model for authentication and data handling
│   ├── routes                # Contains route definitions
│   │   ├── __init__.py       # Initializes routes package
│   │   ├── auth.py           # Authentication routes (login, registration)
│   │   ├── file.py           # File handling routes (upload, download)
│   │   └── chat.py           # Chat message routes (send, retrieve)
│   ├── utils                 # Utility functions
│   │   ├── __init__.py       # Initializes utils package
│   │   ├── encryption.py      # Functions for data encryption
│   │   └── validation.py      # Functions for input validation
│   ├── static                # Static files (CSS, JS, images)
│   └── uploads               # Directory for uploaded files
├── client
│   ├── main.py               # Entry point for the Tkinter client
│   ├── gui                   # GUI components
│   │   ├── __init__.py       # Initializes GUI package
│   │   ├── login.py          # Login interface
│   │   ├── chat.py           # Chat interface
│   │   ├── file_upload.py     # File upload interface
│   │   └── profile.py        # Profile management interface
│   ├── utils                 # Client utility functions
│   │   ├── __init__.py       # Initializes client utils package
│   │   ├── api_requests.py    # Functions for HTTP requests to the server
│   │   └── encryption.py      # Functions for client-side data encryption
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Features

- **User Registration and Login**: Users can create accounts and log in securely.
- **File Upload and Download**: Users can upload files to the server and download files shared by others.
- **Chat Functionality**: Users can send and receive messages in real-time.
- **Secure Data Handling**: Sensitive data is encrypted and stored securely.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd file-sharing-chat-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the Flask server:
   ```
   python server/app.py
   ```

4. In a separate terminal, run the Tkinter client:
   ```
   python client/main.py
   ```

## Usage

- **Register**: Create a new account using the registration interface.
- **Login**: Use your credentials to log in to the application.
- **Upload Files**: Navigate to the file upload interface to share files.
- **Chat**: Use the chat interface to communicate with other users.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.