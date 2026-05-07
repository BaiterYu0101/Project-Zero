This .md is use for services.yaml documentation to have a better understanding on it

Same as the deployment, it have AKMS:
    A = apiVersion
    K = kind
    M = metadata
    S = spec

The apiVersion for services.yaml is: v1
The kind is call Service
Metadata, just put the name of it

Spec have three:
    S = selector
    T = the service type    
        - Consiste of four:: which are,
            - ClusterIP
            - NodePort
            - LoadBalancer (usually use this to talk to external in a cloud services)
            - ExternalName
    P = ports
        - it consists of the protocol and also the port and targetPort