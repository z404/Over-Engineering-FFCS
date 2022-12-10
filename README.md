# Over Engineering FFCS

## Build image

To build dockerfile

```bash
docker build -t oeffcs .
```

You can use [build args](https://vsupalov.com/docker-arg-env-variable-guide/) for different admin credentials although the defaults of:

| category |       value        |
|   ---    |        ---         |
| Username |       admin        |
| Password |      admin123      |
|  Email   |  admin@example.com |

## Run with volumes

```bash
docker run -d \
    -p 80:8000 \
    -v :/home
    oeffcs
```
