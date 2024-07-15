from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'CLIENT': {
            'host': 'mongodb+srv://limechat:gstVlbIXstl68El9@cluster0.dvgmkyc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0',
            'port': 27017,
            'username': 'limechat',
            'password': 'gstVlbIXstl68El9',
            'authSource': 'admin',
        },
        'NAME': 'Cluster0',
    }
}
