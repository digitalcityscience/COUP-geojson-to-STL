FROM publysher/alpine-numpy
WORKDIR /usr/src/app
RUN mkdir buildings

RUN pip3 install --no-cache-dir stl numpy-stl

COPY . /usr/src/app

ENTRYPOINT ["python", "./main.py" ]

# RUN WITH buildings folder as a VOLUME 
# docker run -v buildings:/usr/src/app/buildings .