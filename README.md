# SongSnake

SongSnake is a music player that receives data via a socket connection. The music files are stored on the server and sent to the client through a TCP/IP connection.

## Installation

1. Make sure you have Python installed on your system.

2. Clone this repository to your local machine.

3. Open a terminal or command prompt and navigate to the project directory.

4. Run the following command to install the required dependencies: 

```pip install -r requirements.txt```

5. Add your MP3 audio files to the 'new_audio' folder in the project directory.

6. Run the 'file_convert.py' script to convert the MP3 files to WAV format:

```python file_convert.py```


## Usage

1. Open a terminal or command prompt and navigate to the project directory.

2. Start the server by running the following command:

```python server.py```

3. In another terminal or command prompt, start the client by running the following command:

```python client.py```

4. Once the client is running, you can use the GUI interface to browse and play the available music files.

## Additional Notes

- Make sure that the server and client are running on the same network or have access to each other's IP address.

- The converted WAV files will be stored in the 'resource' folder.

- You can customize the appearance of the GUI interface by modifying the provided images in the 'assets' folder.

- Feel free to add more MP3 audio files to the 'new_audio' folder and run the 'file_convert.py' script to convert them.

- If you encounter any issues or errors, please check the troubleshooting section in this README file or contact the project maintainers.

## Troubleshooting

- If you are experiencing connection issues, ensure that any firewalls or network restrictions are not blocking the necessary ports for the server and client communication.

- If you encounter any errors related to missing dependencies, please make sure you have installed all the required packages as mentioned in the Installation section.

- For further assistance or bug reporting, please contact the project maintainers or open an issue in the project's GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).