# KnEDLe - DODFMiner

## Requirements

Tesseract
MuPDF
pdfinfo

## Usage
Run the following in the command line:

```pip3 install -r requeriments.txt```

To run Jupyter, use the command line:

```jupyter notebook```

Will be opened:

```localhost:8888tree```

## Using Docker
Since this project have several dependencies outside Python libraries, there is
a DockerFile and a Compose file provided to facilitate the correct execution of
this project. The DockerFile contains instructions on how the image is build,
while the Compose file contains instruction on how to run the image.

The container created by the image in DockerFile use a DATA_PATH environment
variable as the location to save the downloaded DODF PDFs and the extracted JSONs.

To build and execute the image the docker and docker-compose
need to be correct installed:

1. [Install Docker](https://docs.docker.com/compose/environment-variables/)

2. [Install Docker Compose](https://docs.docker.com/compose/install/)

After the installation, the first thing that docker needs is and image. To create the image run in the root of the project:

```sh
docker-compose build
```

This can took a while to finish.

Now, with the image created, the docker-compose can generate instances (containers) of this image to run specifics tasks.

![image](./dodfminer-docker.jpg)

```sh
DATA_PATH=/path/to/save/files/ \
sudo -E docker-compose run dodfminer -sd 01/19 -ed 01/19
```
This command executes the download task, where -st is the start date and -ed the end date, representing the interval that the DODFs will be downloaded.

Other arguments can be found excuting the command:

```sh
DATA_PATH=/path/to/save/files/ \
sudo -E docker-compose run dodfminer --help
```
Note that if your docker is already in the _sudo_ group you can
execute without _sudo_, otherwise the -E argument is needed for
_sudo_ use the environment variables declared in login _bash_.

## Docs and Code Guidelines

http://google.github.io/styleguide/pyguide.html

## Test

https://docs.pytest.org/en/latest/
