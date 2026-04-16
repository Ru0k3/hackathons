# AnyBook Library App

An Android application that helps users discover books online, save them for later, organize their personal collection, and share books with friends. The app requires an internet connection to open and access book content, and it uses Firebase Authentication for user login. 

## Features

- Firebase Authentication for secure login and signup
- Browse and discover books online
- Search and filter books by title, author, genre, and language
- Save books to read again later
- Manage your personal library
- Favorites, bookmarks, and reading history
- Share books with friends
- Internet connection required to open and read books

## Tech Stack

- **Language:** Java
- **Platform:** Android
- **Authentication:** Firebase Authentication
- **Build System:** Gradle

## Project Structure

```bash
LoginActivity/
├── app/
├── gradle/
├── build.gradle
├── gradle.properties
├── settings.gradle
├── gradlew
└── gradlew.bat
```

## Requirements

- Android Studio
- Android device or emulator
- Internet connection
- Firebase project configuration

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/R-Krishna-F1/LoginActivity.git
   ```

2. Open the project in Android Studio.

3. Connect the project to Firebase:
   - Create a Firebase project
   - Enable Authentication
   - Add your `google-services.json` file inside the `app/` directory

4. Sync Gradle files.

5. Run the app on an emulator or physical Android device.

## App Workflow

1. Users sign up or log in using Firebase Authentication.
2. They can browse available books from the app.
3. Users can search and filter books based on title, author, genre, and language.
4. Books can be added to favorites, bookmarked, or saved for later reading.
5. Users can manage their personal library and revisit reading history.
6. Books can be shared with friends from inside the app.
7. The app needs an internet connection to open and access books.

## Use Cases

- Discover books across different categories
- Save favorite books for later reading
- Track bookmarked and previously viewed books
- Organize a personal digital library
- Share reading suggestions with friends

## Future Improvements

- Personalized book recommendations
- Dark mode support
- Offline caching for saved books
- Reading progress tracker
- User profile and reading statistics
- Reviews and ratings
- Admin dashboard for adding or updating books

## Author

Developed by **R-Krishna-F1**

## License

This project is open source. You can add a license such as MIT if you want to make usage terms clear.
