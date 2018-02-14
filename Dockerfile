

FROM python:3.6

RUN pip install cryptography
RUN pip install pyperclip
RUN pip install https://github.com/jonathanslenders/python-prompt-toolkit/archive/2.0.zip

ENV TERM xterm  

WORKDIR /clipwdmgr

RUN mkdir clipwdmgr

ADD ./clipwdmgr2/*.py ./clipwdmgr2/

ADD ./clipwdmgr2-runner.py .

#copy to clipboard does not work from container

CMD ["/bin/bash"]
